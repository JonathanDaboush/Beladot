import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Nav, Alert, Form, Modal } from 'react-bootstrap';
import sellerService from '../services/sellerService';
import { TableSkeleton } from '../components/common/LoadingSkeleton';
import { EmptyProductsState } from '../components/common/EmptyState';
import { useKeyboardShortcuts, SHORTCUTS } from '../utils/keyboardShortcuts';
import { formatCurrency, formatDate, getInventoryStatus } from '../utils/formatters';
import { useToast } from '../contexts/ToastContext';

/**
 * Seller Portal (Amazon Seller Central Style)
 * Product management, sales analytics, order fulfillment
 * Available to: SELLER role only
 */
const SellerPortal = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [sellerInfo, setSellerInfo] = useState(null);
  const [salesReport, setSalesReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showProductModal, setShowProductModal] = useState(false);
  const toast = useToast();

  // Keyboard shortcuts
  const shortcuts = [
    { ...SHORTCUTS.SELLER.NEW_PRODUCT, callback: () => setShowProductModal(true) },
    { ...SHORTCUTS.SELLER.DASHBOARD, callback: () => setActiveTab('dashboard') },
    { ...SHORTCUTS.SELLER.VIEW_ORDERS, callback: () => setActiveTab('orders') },
  ];
  useKeyboardShortcuts(shortcuts, []);

  useEffect(() => {
    loadSellerData();
  }, [activeTab]);

  const loadSellerData = async () => {
    try {
      setLoading(true);
      setError(null);

      if (activeTab === 'dashboard') {
        const [info, report] = await Promise.all([
          sellerService.getSellerInfo(),
          sellerService.getSalesReport(),
        ]);
        setSellerInfo(info);
        setSalesReport(report);
      } else if (activeTab === 'products') {
        const data = await sellerService.getMyProducts();
        setProducts(data.items || data || []);
      } else if (activeTab === 'orders') {
        const data = await sellerService.getOrders();
        setOrders(data.items || data || []);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load data');
      toast.error('Failed to load seller data');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;

    try {
      await sellerService.deleteProduct(productId);
      setProducts(products.filter((p) => p.id !== productId));
      toast.success('Product deleted successfully');
    } catch (err) {
      toast.error('Failed to delete product');
    }
  };

  const handleUpdateStock = async (productId, newStock) => {
    try {
      await sellerService.updateProductStock(productId, newStock);
      setProducts(products.map(p => 
        p.id === productId ? { ...p, quantity: newStock } : p
      ));
      toast.success('Stock updated successfully');
    } catch (err) {
      toast.error('Failed to update stock');
    }
  };

  const renderDashboard = () => (
    <div>
      {/* Stats Cards */}
      <Row xs={1} md={2} lg={4} className="g-4 mb-4">
        <Col>
          <Card className="text-center h-100 border-primary">
            <Card.Body>
              <div className="text-muted mb-2">Total Sales</div>
              <div className="display-6 fw-bold text-primary">
                {formatCurrency(salesReport?.total_sales || 0)}
              </div>
              <small className="text-success">+12% from last month</small>
            </Card.Body>
          </Card>
        </Col>
        <Col>
          <Card className="text-center h-100 border-success">
            <Card.Body>
              <div className="text-muted mb-2">Total Orders</div>
              <div className="display-6 fw-bold text-success">
                {salesReport?.total_orders || 0}
              </div>
              <small className="text-success">+8% from last month</small>
            </Card.Body>
          </Card>
        </Col>
        <Col>
          <Card className="text-center h-100 border-warning">
            <Card.Body>
              <div className="text-muted mb-2">Products Listed</div>
              <div className="display-6 fw-bold text-warning">
                {sellerInfo?.active_products || 0}
              </div>
              <small className="text-muted">Active products</small>
            </Card.Body>
          </Card>
        </Col>
        <Col>
          <Card className="text-center h-100 border-info">
            <Card.Body>
              <div className="text-muted mb-2">Seller Rating</div>
              <div className="display-6 fw-bold text-info">
                {sellerInfo?.rating?.toFixed(1) || 'N/A'}
              </div>
              <small className="text-muted">Out of 5.0</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Card className="mb-4">
        <Card.Header className="bg-light">
          <strong>Quick Actions</strong>
        </Card.Header>
        <Card.Body>
          <div className="d-flex gap-2 flex-wrap">
            <Button variant="primary" onClick={() => setShowProductModal(true)}>
              + Add New Product
            </Button>
            <Button variant="outline-primary" onClick={() => setActiveTab('products')}>
              Manage Inventory
            </Button>
            <Button variant="outline-primary" onClick={() => setActiveTab('orders')}>
              View Orders
            </Button>
            <Button variant="outline-secondary">
              Download Sales Report
            </Button>
          </div>
        </Card.Body>
      </Card>

      {/* Recent Activity */}
      <Card>
        <Card.Header className="bg-light">
          <strong>Recent Orders</strong>
        </Card.Header>
        <Card.Body>
          <p className="text-muted">Your recent order activity will appear here</p>
        </Card.Body>
      </Card>
    </div>
  );

  return (
    <Container fluid className="py-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="mb-0">Seller Central</h1>
          <p className="text-muted mb-0">Manage your products and sales</p>
        </div>
        <Badge bg="primary" className="fs-6 px-3 py-2">
          {sellerInfo?.business_name || 'Seller Account'}
        </Badge>
      </div>

      {/* Navigation Tabs */}
      <Nav variant="tabs" className="mb-4">
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'dashboard'}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'products'}
            onClick={() => setActiveTab('products')}
          >
            📦 Inventory
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'orders'}
            onClick={() => setActiveTab('orders')}
          >
            🛒 Orders
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'analytics'}
            onClick={() => setActiveTab('analytics')}
          >
            📈 Analytics
          </Nav.Link>
        </Nav.Item>
      </Nav>

      {/* Content */}
      {error && <Alert variant="danger" dismissible onClose={() => setError(null)}>{error}</Alert>}

      {loading ? (
        <TableSkeleton rows={5} />
      ) : (
        <>
          {activeTab === 'dashboard' && renderDashboard()}

          {activeTab === 'products' && (
            <div>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h2>Product Inventory</h2>
                <Button variant="primary" onClick={() => setShowProductModal(true)}>
                  + Add Product (Ctrl+N)
                </Button>
              </div>

              {products.length === 0 ? (
                <EmptyProductsState 
                  message="No products yet. Start selling by adding your first product!"
                  action={() => setShowProductModal(true)}
                />
              ) : (
                <Card>
                  <Table responsive hover className="mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Product</th>
                        <th>SKU</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>Status</th>
                        <th>Last Updated</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {products.map((product) => {
                        const stockStatus = getInventoryStatus(product.quantity);
                        return (
                          <tr key={product.id}>
                            <td>
                              <div className="d-flex align-items-center">
                                <div 
                                  className="bg-light me-2 rounded"
                                  style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                                >
                                  📦
                                </div>
                                <div>
                                  <strong>{product.name}</strong>
                                  <div className="small text-muted">{product.description?.substring(0, 50)}...</div>
                                </div>
                              </div>
                            </td>
                            <td><code>{product.sku || 'N/A'}</code></td>
                            <td><strong>{formatCurrency(product.price)}</strong></td>
                            <td>
                              <Badge bg={stockStatus.color}>{stockStatus.text}</Badge>
                              <Form.Control 
                                type="number" 
                                size="sm" 
                                className="mt-1" 
                                style={{ width: '80px' }}
                                defaultValue={product.quantity}
                                onBlur={(e) => {
                                  const newStock = parseInt(e.target.value);
                                  if (newStock !== product.quantity) {
                                    handleUpdateStock(product.id, newStock);
                                  }
                                }}
                              />
                            </td>
                            <td>
                              {product.is_active ? (
                                <Badge bg="success">Active</Badge>
                              ) : (
                                <Badge bg="secondary">Inactive</Badge>
                              )}
                            </td>
                            <td>{formatDate(product.updated_at)}</td>
                            <td>
                              <Button 
                                variant="link" 
                                size="sm" 
                                className="p-0 me-2"
                                title="Edit"
                              >
                                ✏️
                              </Button>
                              <Button
                                variant="link"
                                size="sm"
                                className="p-0 text-danger"
                                title="Delete"
                                onClick={() => handleDeleteProduct(product.id)}
                              >
                                🗑️
                              </Button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </Table>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'orders' && (
            <Card>
              <Card.Body className="text-center p-5">
                <h2>Order Fulfillment</h2>
                <p className="text-muted">View and manage orders containing your products</p>
                <Badge bg="info">Coming Soon</Badge>
              </Card.Body>
            </Card>
          )}

          {activeTab === 'analytics' && (
            <Card>
              <Card.Body className="text-center p-5">
                <h2>Advanced Analytics</h2>
                <p className="text-muted">Detailed sales reports and performance metrics</p>
                <Badge bg="info">Coming Soon</Badge>
              </Card.Body>
            </Card>
          )}
        </>
      )}

      {/* Add Product Modal (placeholder) */}
      <Modal show={showProductModal} onHide={() => setShowProductModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Add New Product</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p className="text-muted">Product creation form will be implemented here</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowProductModal(false)}>
            Cancel
          </Button>
          <Button variant="primary">
            Create Product
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default SellerPortal;
