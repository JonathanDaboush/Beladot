import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Badge, Nav, Form, Modal, Alert } from 'react-bootstrap';
import transportService from '../services/transportService';
import { TableSkeleton } from '../components/common/LoadingSkeleton';
import { EmptyShipmentsState } from '../components/common/EmptyState';
import { useKeyboardShortcuts, SHORTCUTS } from '../utils/keyboardShortcuts';
import { formatDate, formatRelativeTime, getShipmentStatusBadge } from '../utils/formatters';
import { useToast } from '../contexts/ToastContext';

/**
 * Transport Console (ShipStation-style)
 * Logistics, shipping management, returns processing, inventory
 * Available to: TRANSPORT, TRANSPORT_MANAGER roles only
 * CRITICAL: NO payment or financial access (department boundary)
 */
const TransportConsole = () => {
  const [activeTab, setActiveTab] = useState('shipments');
  const [shipments, setShipments] = useState([]);
  const [returns, setReturns] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [showShipmentModal, setShowShipmentModal] = useState(false);
  const [showScanModal, setShowScanModal] = useState(false);
  const [barcodeInput, setBarcodeInput] = useState('');
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  // Keyboard shortcuts
  const shortcuts = [
    { ...SHORTCUTS.TRANSPORT.SHIPMENTS, callback: () => setActiveTab('shipments') },
    { ...SHORTCUTS.TRANSPORT.SCAN_BARCODE, callback: () => setShowScanModal(true) },
  ];
  useKeyboardShortcuts(shortcuts, []);

  useEffect(() => {
    loadTransportData();
  }, [activeTab]);

  const loadTransportData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'shipments') {
        const data = await transportService.getShipments();
        setShipments(data.items || data || []);
      } else if (activeTab === 'returns') {
        const data = await transportService.getReturns();
        setReturns(data.items || data || []);
      } else if (activeTab === 'inventory') {
        const data = await transportService.getInventory();
        setInventory(data.items || data || []);
      }
    } catch (err) {
      toast.error('Failed to load transport data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateShipmentStatus = async (shipmentId, newStatus) => {
    try {
      await transportService.updateShipmentStatus(shipmentId, newStatus);
      toast.success(`Shipment status updated to ${newStatus}`);
      loadTransportData();
    } catch (err) {
      toast.error('Failed to update shipment status');
    }
  };

  const handleReceiveReturn = async (returnId) => {
    try {
      await transportService.receiveReturn(returnId);
      toast.success('Return received and inventory updated');
      loadTransportData();
    } catch (err) {
      toast.error('Failed to process return');
    }
  };

  const handleAdjustStock = async (productId, quantity, reason) => {
    try {
      await transportService.adjustProductStock(productId, quantity, reason);
      toast.success('Stock adjusted successfully');
      loadTransportData();
    } catch (err) {
      toast.error('Failed to adjust stock');
    }
  };

  const handleBarcodeScan = async () => {
    if (!barcodeInput.trim()) return;

    try {
      // Simulate barcode lookup - replace with actual service call
      toast.success(`Barcode scanned: ${barcodeInput}`);
      setBarcodeInput('');
      setShowScanModal(false);
    } catch (err) {
      toast.error('Barcode not found');
    }
  };

  const renderShipmentsTab = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>Shipment Queue</h4>
        <div className="d-flex gap-2">
          <Button variant="primary" onClick={() => setShowScanModal(true)}>
            📷 Scan Barcode (Ctrl+B)
          </Button>
          <Button variant="outline-primary" onClick={loadTransportData}>
            🔄 Refresh
          </Button>
        </div>
      </div>

      {/* Status Summary */}
      <Row xs={2} md={4} className="g-3 mb-4">
        <Col>
          <Card className="text-center border-warning">
            <Card.Body className="py-2">
              <div className="h3 mb-0 text-warning">
                {shipments.filter(s => s.status === 'PENDING').length}
              </div>
              <small className="text-muted">Pending Pickup</small>
            </Card.Body>
          </Card>
        </Col>
        <Col>
          <Card className="text-center border-info">
            <Card.Body className="py-2">
              <div className="h3 mb-0 text-info">
                {shipments.filter(s => s.status === 'IN_TRANSIT').length}
              </div>
              <small className="text-muted">In Transit</small>
            </Card.Body>
          </Card>
        </Col>
        <Col>
          <Card className="text-center border-primary">
            <Card.Body className="py-2">
              <div className="h3 mb-0 text-primary">
                {shipments.filter(s => s.status === 'OUT_FOR_DELIVERY').length}
              </div>
              <small className="text-muted">Out for Delivery</small>
            </Card.Body>
          </Card>
        </Col>
        <Col>
          <Card className="text-center border-success">
            <Card.Body className="py-2">
              <div className="h3 mb-0 text-success">
                {shipments.filter(s => s.status === 'DELIVERED').length}
              </div>
              <small className="text-muted">Delivered</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {loading ? (
        <TableSkeleton rows={10} />
      ) : shipments.length === 0 ? (
        <EmptyShipmentsState />
      ) : (
        <Card>
          <Table responsive hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Tracking #</th>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Destination</th>
                <th>Carrier</th>
                <th>Status</th>
                <th>Shipped</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {shipments.map((shipment) => {
                const statusBadge = getShipmentStatusBadge(shipment.status);
                return (
                  <tr key={shipment.id}>
                    <td>
                      <code>{shipment.tracking_number}</code>
                    </td>
                    <td><small>{shipment.order_id?.substring(0, 8)}</small></td>
                    <td>{shipment.customer_name || 'N/A'}</td>
                    <td>{shipment.destination_city}, {shipment.destination_state}</td>
                    <td>
                      <Badge bg="secondary">{shipment.carrier || 'USPS'}</Badge>
                    </td>
                    <td>
                      <Badge bg={statusBadge.color}>{statusBadge.text}</Badge>
                    </td>
                    <td>{formatRelativeTime(shipment.shipped_at)}</td>
                    <td>
                      <div className="d-flex gap-1">
                        {shipment.status === 'PENDING' && (
                          <Button
                            variant="link"
                            size="sm"
                            className="p-0"
                            onClick={() => handleUpdateShipmentStatus(shipment.id, 'IN_TRANSIT')}
                          >
                            🚚 Ship
                          </Button>
                        )}
                        {shipment.status === 'IN_TRANSIT' && (
                          <Button
                            variant="link"
                            size="sm"
                            className="p-0"
                            onClick={() => handleUpdateShipmentStatus(shipment.id, 'OUT_FOR_DELIVERY')}
                          >
                            📦 Out for Delivery
                          </Button>
                        )}
                        {shipment.status === 'OUT_FOR_DELIVERY' && (
                          <Button
                            variant="link"
                            size="sm"
                            className="p-0"
                            onClick={() => handleUpdateShipmentStatus(shipment.id, 'DELIVERED')}
                          >
                            ✅ Delivered
                          </Button>
                        )}
                        <Button
                          variant="link"
                          size="sm"
                          className="p-0 ms-2"
                          onClick={() => {
                            setSelectedShipment(shipment);
                            setShowShipmentModal(true);
                          }}
                        >
                          📝 Notes
                        </Button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        </Card>
      )}
    </div>
  );

  const renderReturnsTab = () => (
    <div>
      <h4 className="mb-3">Returns Processing</h4>

      {loading ? (
        <TableSkeleton rows={10} />
      ) : returns.length === 0 ? (
        <Card className="text-center py-5">
          <Card.Body>
            <div style={{ fontSize: '4rem' }}>📦</div>
            <h5 className="mt-3">No Returns</h5>
            <p className="text-muted">Returns to process will appear here</p>
          </Card.Body>
        </Card>
      ) : (
        <Card>
          <Table responsive hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Return ID</th>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Product</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Requested</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {returns.map((returnItem) => (
                <tr key={returnItem.id}>
                  <td><code>{returnItem.id.substring(0, 8)}</code></td>
                  <td><small>{returnItem.order_id?.substring(0, 8)}</small></td>
                  <td>{returnItem.customer_name}</td>
                  <td>{returnItem.product_name}</td>
                  <td><small className="text-muted">{returnItem.reason}</small></td>
                  <td>
                    {returnItem.status === 'APPROVED' ? (
                      <Badge bg="success">Approved</Badge>
                    ) : returnItem.status === 'RECEIVED' ? (
                      <Badge bg="info">Received</Badge>
                    ) : (
                      <Badge bg="warning">Pending</Badge>
                    )}
                  </td>
                  <td>{formatDate(returnItem.created_at)}</td>
                  <td>
                    {returnItem.status === 'APPROVED' && (
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0"
                        onClick={() => handleReceiveReturn(returnItem.id)}
                      >
                        📥 Receive
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
    </div>
  );

  const renderInventoryTab = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>Inventory Management</h4>
        <div className="d-flex gap-2">
          <Button variant="outline-primary">📥 Import</Button>
          <Button variant="outline-primary">📤 Export</Button>
        </div>
      </div>

      {loading ? (
        <TableSkeleton rows={10} />
      ) : inventory.length === 0 ? (
        <Card className="text-center py-5">
          <Card.Body>
            <div style={{ fontSize: '4rem' }}>📦</div>
            <h5 className="mt-3">No Inventory Data</h5>
          </Card.Body>
        </Card>
      ) : (
        <Card>
          <Table responsive hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>SKU</th>
                <th>Product Name</th>
                <th>Location</th>
                <th>In Stock</th>
                <th>Reserved</th>
                <th>Available</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {inventory.map((item) => (
                <tr key={item.id}>
                  <td><code>{item.sku}</code></td>
                  <td><strong>{item.product_name}</strong></td>
                  <td>{item.warehouse_location || 'Main'}</td>
                  <td>{item.quantity_in_stock || 0}</td>
                  <td>{item.quantity_reserved || 0}</td>
                  <td>
                    <strong className={item.quantity_available < 10 ? 'text-danger' : 'text-success'}>
                      {item.quantity_available || 0}
                    </strong>
                  </td>
                  <td>
                    <Button variant="link" size="sm" className="p-0">
                      ✏️ Adjust
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
    </div>
  );

  return (
    <Container fluid className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>🚚 Transport Console</h1>
          <p className="text-muted mb-0">ShipStation-style logistics management</p>
        </div>
        <Alert variant="info" className="mb-0 py-2">
          <small><strong>Department Boundary:</strong> No payment/financial access</small>
        </Alert>
      </div>

      {/* Navigation Tabs */}
      <Nav variant="tabs" className="mb-4">
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'shipments'}
            onClick={() => setActiveTab('shipments')}
          >
            📦 Shipments (Ctrl+S)
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'returns'}
            onClick={() => setActiveTab('returns')}
          >
            ↩️ Returns
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'inventory'}
            onClick={() => setActiveTab('inventory')}
          >
            📊 Inventory
          </Nav.Link>
        </Nav.Item>
      </Nav>

      {/* Content */}
      {activeTab === 'shipments' && renderShipmentsTab()}
      {activeTab === 'returns' && renderReturnsTab()}
      {activeTab === 'inventory' && renderInventoryTab()}

      {/* Shipment Notes Modal */}
      <Modal show={showShipmentModal} onHide={() => setShowShipmentModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Shipment Notes</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedShipment && (
            <div>
              <p><strong>Tracking:</strong> {selectedShipment.tracking_number}</p>
              <Form.Group>
                <Form.Label>Add Note</Form.Label>
                <Form.Control as="textarea" rows={3} placeholder="Add shipping notes..." />
              </Form.Group>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowShipmentModal(false)}>
            Close
          </Button>
          <Button variant="primary">Save Note</Button>
        </Modal.Footer>
      </Modal>

      {/* Barcode Scanner Modal */}
      <Modal show={showScanModal} onHide={() => setShowScanModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>📷 Scan Barcode</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group>
            <Form.Label>Enter or Scan Barcode</Form.Label>
            <Form.Control
              type="text"
              placeholder="Scan barcode or enter tracking number..."
              value={barcodeInput}
              onChange={(e) => setBarcodeInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleBarcodeScan()}
              autoFocus
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowScanModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleBarcodeScan}>
            Lookup
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default TransportConsole;
