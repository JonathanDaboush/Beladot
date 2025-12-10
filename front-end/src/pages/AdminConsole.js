import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Badge, Nav, Form, Modal, Alert, Tabs, Tab } from 'react-bootstrap';
import adminService from '../services/adminService';
import { useFeatureFlags } from '../contexts/FeatureFlagContext';
import { TableSkeleton } from '../components/common/LoadingSkeleton';
import { formatDate, formatRelativeTime } from '../utils/formatters';
import { getRoleDisplayName, getRoleBadgeColor } from '../utils/roleHelper';
import { useToast } from '../contexts/ToastContext';

/**
 * Admin Console (AWS Console-style Tabs)
 * Full system access - user management, system config, ALL operations
 * Available to: ADMIN role only
 * CRITICAL: Complete system control with audit logging
 */
const AdminConsole = () => {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [apiKeys, setApiKeys] = useState([]);
  const [systemConfig, setSystemConfig] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const { flags, toggleFlag } = useFeatureFlags();
  const toast = useToast();

  useEffect(() => {
    loadAdminData();
  }, [activeTab]);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'users') {
        const data = await adminService.getAllUsers();
        setUsers(data.items || data || []);
      } else if (activeTab === 'products') {
        const data = await adminService.getAllProducts();
        setProducts(data.items || data || []);
      } else if (activeTab === 'orders') {
        const data = await adminService.getAllOrders();
        setOrders(data.items || data || []);
      } else if (activeTab === 'audit') {
        const data = await adminService.getAuditLogs();
        setAuditLogs(data.items || data || []);
      } else if (activeTab === 'apikeys') {
        const data = await adminService.getApiKeys();
        setApiKeys(data || []);
      } else if (activeTab === 'config') {
        const data = await adminService.getSystemConfig();
        setSystemConfig(data);
      }
    } catch (err) {
      toast.error('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUserRole = async (userId, newRole) => {
    try {
      await adminService.updateUserRole(userId, newRole);
      toast.success('User role updated');
      loadAdminData();
    } catch (err) {
      toast.error('Failed to update user role');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      await adminService.deleteUser(userId);
      toast.success('User deleted');
      loadAdminData();
    } catch (err) {
      toast.error('Failed to delete user');
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    
    try {
      await adminService.deleteAnyProduct(productId);
      toast.success('Product deleted');
      loadAdminData();
    } catch (err) {
      toast.error('Failed to delete product');
    }
  };

  const handleCreateApiKey = async (keyData) => {
    try {
      const result = await adminService.createApiKey(keyData);
      toast.success('API key created');
      setShowModal(false);
      loadAdminData();
    } catch (err) {
      toast.error('Failed to create API key');
    }
  };

  const renderUsersTab = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>User Management</h4>
        <Button variant="primary" onClick={() => {
          setModalType('create_user');
          setShowModal(true);
        }}>
          + Create User
        </Button>
      </div>

      {loading ? (
        <TableSkeleton rows={10} />
      ) : (
        <Card>
          <Table responsive hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Role</th>
                <th>Created</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>
                    <strong>{user.first_name} {user.last_name}</strong>
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <Badge bg={getRoleBadgeColor(user.role)}>
                      {getRoleDisplayName(user.role)}
                    </Badge>
                  </td>
                  <td>{formatDate(user.created_at)}</td>
                  <td>
                    <Badge bg={user.is_active ? 'success' : 'secondary'}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </td>
                  <td>
                    <Button variant="link" size="sm" className="p-0 me-2">
                      ✏️ Edit
                    </Button>
                    <Button
                      variant="link"
                      size="sm"
                      className="p-0 text-danger"
                      onClick={() => handleDeleteUser(user.id)}
                    >
                      🗑️ Delete
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

  const renderProductsTab = () => (
    <div>
      <h4 className="mb-3">All Products (All Sellers)</h4>

      {loading ? (
        <TableSkeleton rows={10} />
      ) : (
        <Card>
          <Table responsive hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Product</th>
                <th>Seller</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td><strong>{product.name}</strong></td>
                  <td>{product.seller_name || 'N/A'}</td>
                  <td>${product.price}</td>
                  <td>{product.quantity}</td>
                  <td>
                    <Badge bg={product.is_active ? 'success' : 'secondary'}>
                      {product.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </td>
                  <td>
                    <Button variant="link" size="sm" className="p-0 me-2">
                      ✏️ Edit
                    </Button>
                    <Button
                      variant="link"
                      size="sm"
                      className="p-0 text-danger"
                      onClick={() => handleDeleteProduct(product.id)}
                    >
                      🗑️ Delete
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

  const renderOrdersTab = () => (
    <div>
      <h4 className="mb-3">All Orders (System-wide)</h4>

      {loading ? (
        <TableSkeleton rows={10} />
      ) : (
        <Card>
          <Table responsive hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Total</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>
                  <td><code>{order.id.substring(0, 8)}</code></td>
                  <td>{order.customer_name || order.user_email}</td>
                  <td><strong>${order.total}</strong></td>
                  <td><Badge>{order.status}</Badge></td>
                  <td>{formatDate(order.created_at)}</td>
                  <td>
                    <Button variant="link" size="sm" className="p-0">
                      👁️ View
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

  const renderAuditTab = () => (
    <div>
      <h4 className="mb-3">Audit Logs</h4>

      {loading ? (
        <TableSkeleton rows={10} />
      ) : (
        <Card>
          <Table responsive hover size="sm" className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Timestamp</th>
                <th>User</th>
                <th>Action</th>
                <th>Entity</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map((log) => (
                <tr key={log.id}>
                  <td>{formatRelativeTime(log.created_at)}</td>
                  <td><Badge bg="info">{log.user_email}</Badge></td>
                  <td><Badge bg="secondary">{log.action_type}</Badge></td>
                  <td>{log.entity_type} #{log.entity_id?.substring(0, 8)}</td>
                  <td><small className="text-muted">{log.details}</small></td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
    </div>
  );

  const renderApiKeysTab = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>API Keys</h4>
        <Button variant="primary" onClick={() => {
          setModalType('create_api_key');
          setShowModal(true);
        }}>
          + Create API Key
        </Button>
      </div>

      {loading ? (
        <TableSkeleton rows={5} />
      ) : (
        <Card>
          <Table responsive hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Name</th>
                <th>Key</th>
                <th>Created</th>
                <th>Last Used</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {apiKeys.map((key) => (
                <tr key={key.id}>
                  <td><strong>{key.name}</strong></td>
                  <td><code>{key.key_preview}***</code></td>
                  <td>{formatDate(key.created_at)}</td>
                  <td>{key.last_used_at ? formatRelativeTime(key.last_used_at) : 'Never'}</td>
                  <td>
                    <Badge bg={key.is_active ? 'success' : 'danger'}>
                      {key.is_active ? 'Active' : 'Revoked'}
                    </Badge>
                  </td>
                  <td>
                    <Button
                      variant="link"
                      size="sm"
                      className="p-0 text-danger"
                      onClick={() => adminService.revokeApiKey(key.id).then(loadAdminData)}
                    >
                      🗑️ Revoke
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

  const renderConfigTab = () => (
    <div>
      <h4 className="mb-4">System Configuration</h4>

      {/* Feature Flags */}
      <Card className="mb-4">
        <Card.Header className="bg-light">
          <strong>🚩 Feature Flags</strong>
        </Card.Header>
        <Card.Body>
          <Row xs={1} md={2} className="g-3">
            {Object.entries(flags).map(([key, value]) => (
              <Col key={key}>
                <Form.Check
                  type="switch"
                  id={`flag-${key}`}
                  label={key.replace(/_/g, ' ').replace(/ENABLE /g, '')}
                  checked={value}
                  onChange={() => toggleFlag(key)}
                />
              </Col>
            ))}
          </Row>
        </Card.Body>
      </Card>

      {/* System Settings */}
      <Card>
        <Card.Header className="bg-light">
          <strong>⚙️ System Settings</strong>
        </Card.Header>
        <Card.Body>
          <Row className="g-3">
            <Col md={6}>
              <Button variant="outline-primary" className="w-100">
                💳 Configure Payment Gateways
              </Button>
            </Col>
            <Col md={6}>
              <Button variant="outline-primary" className="w-100">
                🚚 Configure Shipping Rates
              </Button>
            </Col>
            <Col md={6}>
              <Button variant="outline-primary" className="w-100">
                💰 Configure Tax Rates
              </Button>
            </Col>
            <Col md={6}>
              <Button variant="outline-primary" className="w-100">
                📧 Configure Email Templates
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    </div>
  );

  return (
    <Container fluid className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>🔧 Admin Console</h1>
          <p className="text-muted mb-0">AWS Console-style system administration</p>
        </div>
        <Alert variant="danger" className="mb-0 py-2">
          <small><strong>⚠️ Full System Access:</strong> All operations are logged</small>
        </Alert>
      </div>

      {/* Tab Navigation */}
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-4"
      >
        <Tab eventKey="users" title="👥 Users">
          {renderUsersTab()}
        </Tab>
        <Tab eventKey="products" title="📦 Products">
          {renderProductsTab()}
        </Tab>
        <Tab eventKey="orders" title="🛒 Orders">
          {renderOrdersTab()}
        </Tab>
        <Tab eventKey="audit" title="📋 Audit Logs">
          {renderAuditTab()}
        </Tab>
        <Tab eventKey="apikeys" title="🔑 API Keys">
          {renderApiKeysTab()}
        </Tab>
        <Tab eventKey="config" title="⚙️ Configuration">
          {renderConfigTab()}
        </Tab>
      </Tabs>

      {/* Create Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {modalType === 'create_user' && 'Create New User'}
            {modalType === 'create_api_key' && 'Create API Key'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {modalType === 'create_user' && (
            <Form>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>First Name</Form.Label>
                    <Form.Control type="text" required />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Last Name</Form.Label>
                    <Form.Control type="text" required />
                  </Form.Group>
                </Col>
              </Row>
              <Form.Group className="mb-3">
                <Form.Label>Email</Form.Label>
                <Form.Control type="email" required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Role</Form.Label>
                <Form.Select required>
                  <option value="CUSTOMER">Customer</option>
                  <option value="SELLER">Seller</option>
                  <option value="EMPLOYEE">Employee</option>
                  <option value="MANAGER">Manager</option>
                  <option value="ADMIN">Admin</option>
                </Form.Select>
              </Form.Group>
            </Form>
          )}

          {modalType === 'create_api_key' && (
            <Form>
              <Form.Group className="mb-3">
                <Form.Label>Key Name</Form.Label>
                <Form.Control type="text" placeholder="My API Key" required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Description</Form.Label>
                <Form.Control as="textarea" rows={2} />
              </Form.Group>
              <Alert variant="info">
                <small>The API key will be shown only once after creation. Save it securely.</small>
              </Alert>
            </Form>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Cancel
          </Button>
          <Button variant="primary">
            Create
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default AdminConsole;
