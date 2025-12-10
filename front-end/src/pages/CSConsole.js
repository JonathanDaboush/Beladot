import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Nav, Alert, Table, Button, Form, Modal, Badge, InputGroup } from 'react-bootstrap';
import customerServiceService from '../services/customerServiceService';
import { TableSkeleton } from '../components/common/LoadingSkeleton';
import { EmptyTicketsState } from '../components/common/EmptyState';
import { useKeyboardShortcuts, SHORTCUTS } from '../utils/keyboardShortcuts';
import { formatCurrency, formatDate, formatRelativeTime, getOrderStatusBadge } from '../utils/formatters';
import { useToast } from '../contexts/ToastContext';

/**
 * Customer Service Console (Zendesk-style Dense UI)
 * Dense ticket management, refund/return approvals with MANDATORY LOGGING
 * Available to: CUSTOMER_SERVICE role only
 * CRITICAL: All actions MUST log via createActionLog()
 */
const CSConsole = () => {
  const [activeTab, setActiveTab] = useState('orders');
  const [users, setUsers] = useState([]);
  const [sellers, setSellers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showActionModal, setShowActionModal] = useState(false);
  const [actionType, setActionType] = useState('');
  const [actionReason, setActionReason] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const toast = useToast();
  const searchInputRef = useRef(null);

  // Keyboard shortcuts (j/k navigation like Gmail/Zendesk)
  const shortcuts = [
    { ...SHORTCUTS.CS.NEXT_TICKET, callback: () => navigateItems(1) },
    { ...SHORTCUTS.CS.PREV_TICKET, callback: () => navigateItems(-1) },
    { ...SHORTCUTS.CS.SEARCH_ORDER, callback: () => { setActiveTab('orders'); setTimeout(() => searchInputRef.current?.focus(), 100); }},
    { ...SHORTCUTS.CS.SEARCH_USER, callback: () => { setActiveTab('users'); setTimeout(() => searchInputRef.current?.focus(), 100); }},
    { ...SHORTCUTS.GLOBAL.SEARCH, callback: () => searchInputRef.current?.focus() },
  ];
  useKeyboardShortcuts(shortcuts, [selectedIndex, activeTab]);

  const navigateItems = (direction) => {
    const currentList = getFilteredData();
    if (currentList.length === 0) return;
    const newIndex = Math.max(0, Math.min(currentList.length - 1, selectedIndex + direction));
    setSelectedIndex(newIndex);
    setSelectedItem(currentList[newIndex]);
  };

  useEffect(() => {
    loadData();
    setSelectedIndex(0);
  }, [activeTab]);

  const loadData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'users') {
        const data = await customerServiceService.getUsers();
        setUsers(data.items || data || []);
      } else if (activeTab === 'sellers') {
        const data = await customerServiceService.getSellers();
        setSellers(data.items || data || []);
      } else if (activeTab === 'orders') {
        const data = await customerServiceService.getOrders();
        setOrders(data.items || data || []);
      }
    } catch (err) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleActionWithLogging = async () => {
    if (!actionReason.trim()) {
      toast.error('Action reason is required for audit logging');
      return;
    }

    try {
      setLoading(true);

      // Perform the action based on type
      if (actionType === 'process_refund') {
        await customerServiceService.processRefund(selectedItem.id, actionReason);
      } else if (actionType === 'approve_return') {
        await customerServiceService.approveReturn(selectedItem.id, actionReason);
      } else if (actionType === 'update_user') {
        await customerServiceService.updateUser(selectedItem.id, { notes: actionReason });
      } else if (actionType === 'update_seller') {
        await customerServiceService.updateSeller(selectedItem.id, { notes: actionReason });
      }

      // MANDATORY: Log the action (CS requirement)
      await customerServiceService.createActionLog({
        action_type: actionType,
        entity_type: activeTab.slice(0, -1), // 'orders' -> 'order'
        entity_id: selectedItem.id,
        details: actionReason,
      });

      toast.success('✅ Action completed and logged');
      setShowActionModal(false);
      setActionReason('');
      loadData(); // Refresh data
    } catch (err) {
      toast.error('Action failed: ' + (err.response?.data?.detail || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const openActionModal = (item, type) => {
    setSelectedItem(item);
    setActionType(type);
    setShowActionModal(true);
  };

  const getFilteredData = () => {
    const currentList = activeTab === 'users' ? users : activeTab === 'sellers' ? sellers : orders;
    if (!searchQuery) return currentList;
    
    return currentList.filter(item => 
      JSON.stringify(item).toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  const displayedData = getFilteredData();

  return (
    <Container fluid className="vh-100 d-flex flex-column" style={{ backgroundColor: '#f8f9fa' }}>
      {/* Header Bar */}
      <div className="bg-dark text-white p-3 d-flex justify-content-between align-items-center">
        <div>
          <h4 className="mb-0">🎧 Customer Service Console</h4>
          <small className="text-muted">Zendesk-style interface with mandatory action logging</small>
        </div>
        <div className="text-end">
          <Badge bg="warning" className="me-2">
            {displayedData.length} items
          </Badge>
          <Badge bg="info">
            Press ? for keyboard shortcuts
          </Badge>
        </div>
      </div>

      {/* Tabs */}
      <Nav variant="tabs" className="bg-white border-bottom">
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'orders'}
            onClick={() => setActiveTab('orders')}
          >
            🛒 Orders (Ctrl+O)
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'users'}
            onClick={() => setActiveTab('users')}
          >
            👥 Users (Ctrl+U)
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'sellers'}
            onClick={() => setActiveTab('sellers')}
          >
            🏪 Sellers
          </Nav.Link>
        </Nav.Item>
      </Nav>

      {/* Search Bar */}
      <div className="bg-white p-2 border-bottom">
        <InputGroup size="sm">
          <InputGroup.Text>🔍</InputGroup.Text>
          <Form.Control
            ref={searchInputRef}
            type="text"
            placeholder="Search... (Press / to focus)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <Button variant="outline-secondary" size="sm" onClick={() => setSearchQuery('')}>
              ✕
            </Button>
          )}
        </InputGroup>
      </div>

      {/* Warning Banner */}
      <Alert variant="warning" className="mb-0 rounded-0 border-0">
        <strong>⚠️ Mandatory Logging:</strong> All CS actions require a reason and are automatically logged for audit. Every action you take is recorded.
      </Alert>

      {/* Main Content */}
      <div className="flex-grow-1 overflow-auto p-3">
        {loading ? (
          <TableSkeleton rows={10} />
        ) : displayedData.length === 0 ? (
          <EmptyTicketsState message="No items found" />
        ) : (
          <div className="bg-white rounded shadow-sm">
            <Table hover size="sm" className="mb-0" style={{ fontSize: '0.9rem' }}>
              <thead className="table-light sticky-top">
                {activeTab === 'orders' && (
                  <tr>
                    <th style={{ width: '40px' }}></th>
                    <th>Order ID</th>
                    <th>Customer</th>
                    <th>Total</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                )}
                {activeTab === 'users' && (
                  <tr>
                    <th style={{ width: '40px' }}></th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Joined</th>
                    <th>Actions</th>
                  </tr>
                )}
                {activeTab === 'sellers' && (
                  <tr>
                    <th style={{ width: '40px' }}></th>
                    <th>Business Name</th>
                    <th>Email</th>
                    <th>Rating</th>
                    <th>Products</th>
                    <th>Actions</th>
                  </tr>
                )}
              </thead>
              <tbody>
                {activeTab === 'orders' && displayedData.map((order, idx) => {
                  const statusBadge = getOrderStatusBadge(order.status);
                  return (
                    <tr 
                      key={order.id}
                      className={selectedIndex === idx ? 'table-active' : ''}
                      onClick={() => { setSelectedIndex(idx); setSelectedItem(order); }}
                      style={{ cursor: 'pointer' }}
                    >
                      <td className="text-center">
                        {selectedIndex === idx && <span>▶</span>}
                      </td>
                      <td><code>{order.id.substring(0, 8)}</code></td>
                      <td>{order.user_email || 'N/A'}</td>
                      <td><strong>{formatCurrency(order.total)}</strong></td>
                      <td><Badge bg={statusBadge.color}>{statusBadge.text}</Badge></td>
                      <td>{formatRelativeTime(order.created_at)}</td>
                      <td>
                        <Button 
                          variant="link" 
                          size="sm" 
                          className="p-0 me-2"
                          onClick={(e) => { e.stopPropagation(); openActionModal(order, 'process_refund'); }}
                        >
                          💰 Refund
                        </Button>
                        <Button 
                          variant="link" 
                          size="sm" 
                          className="p-0"
                          onClick={(e) => { e.stopPropagation(); openActionModal(order, 'approve_return'); }}
                        >
                          📦 Return
                        </Button>
                      </td>
                    </tr>
                  );
                })}
                
                {activeTab === 'users' && displayedData.map((user, idx) => (
                  <tr 
                    key={user.id}
                    className={selectedIndex === idx ? 'table-active' : ''}
                    onClick={() => { setSelectedIndex(idx); setSelectedItem(user); }}
                    style={{ cursor: 'pointer' }}
                  >
                    <td className="text-center">
                      {selectedIndex === idx && <span>▶</span>}
                    </td>
                    <td>{user.first_name} {user.last_name}</td>
                    <td>{user.email}</td>
                    <td><Badge bg="primary">{user.role}</Badge></td>
                    <td>{formatDate(user.created_at)}</td>
                    <td>
                      <Button 
                        variant="link" 
                        size="sm" 
                        className="p-0"
                        onClick={(e) => { e.stopPropagation(); openActionModal(user, 'update_user'); }}
                      >
                        ✏️ Edit
                      </Button>
                    </td>
                  </tr>
                ))}
                
                {activeTab === 'sellers' && displayedData.map((seller, idx) => (
                  <tr 
                    key={seller.id}
                    className={selectedIndex === idx ? 'table-active' : ''}
                    onClick={() => { setSelectedIndex(idx); setSelectedItem(seller); }}
                    style={{ cursor: 'pointer' }}
                  >
                    <td className="text-center">
                      {selectedIndex === idx && <span>▶</span>}
                    </td>
                    <td><strong>{seller.business_name}</strong></td>
                    <td>{seller.email}</td>
                    <td>⭐ {seller.rating?.toFixed(1) || 'N/A'}</td>
                    <td>{seller.product_count || 0}</td>
                    <td>
                      <Button 
                        variant="link" 
                        size="sm" 
                        className="p-0"
                        onClick={(e) => { e.stopPropagation(); openActionModal(seller, 'update_seller'); }}
                      >
                        ✏️ Edit
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        )}

        {/* Navigation hint */}
        {displayedData.length > 0 && (
          <div className="text-center mt-3">
            <small className="text-muted">
              Use <kbd>J</kbd> and <kbd>K</kbd> to navigate • Item {selectedIndex + 1} of {displayedData.length}
            </small>
          </div>
        )}
      </div>

      {/* Action Modal with Mandatory Logging */}
      <Modal show={showActionModal} onHide={() => setShowActionModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>
            {actionType === 'process_refund' && '💰 Process Refund'}
            {actionType === 'approve_return' && '📦 Approve Return'}
            {actionType === 'update_user' && '✏️ Update User'}
            {actionType === 'update_seller' && '✏️ Update Seller'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="info" className="small">
            <strong>📋 Action Logging:</strong> This action will be permanently logged with your user ID, timestamp, and reason.
          </Alert>

          {selectedItem && (
            <div className="mb-3 p-2 bg-light rounded">
              <small><strong>Item:</strong> {selectedItem.id || selectedItem.email || selectedItem.business_name}</small>
            </div>
          )}

          <Form.Group>
            <Form.Label><strong>Reason (Required)*</strong></Form.Label>
            <Form.Control
              as="textarea"
              rows={4}
              placeholder="Explain why you are taking this action (minimum 10 characters)..."
              value={actionReason}
              onChange={(e) => setActionReason(e.target.value)}
              required
            />
            <Form.Text className="text-muted">
              This reason will be visible in audit logs and to managers.
            </Form.Text>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowActionModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={handleActionWithLogging}
            disabled={loading || actionReason.trim().length < 10}
          >
            {loading ? 'Processing...' : 'Confirm & Log Action'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default CSConsole;
