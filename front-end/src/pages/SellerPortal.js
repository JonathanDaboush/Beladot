import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Nav, Alert } from 'react-bootstrap';
import sellerService from '../services/sellerService';
import LoadingSpinner from '../components/common/LoadingSpinner';

/**
 * Seller Portal
 * Product management, sales analytics
 * Available to: SELLER role only
 */
const SellerPortal = () => {
  const [activeTab, setActiveTab] = useState('products');
  const [products, setProducts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSellerData();
  }, [activeTab]);

  const loadSellerData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'products') {
        const data = await sellerService.getSellerProducts();
        setProducts(data.items || []);
      } else if (activeTab === 'analytics') {
        const startDate = new Date();
        startDate.setMonth(startDate.getMonth() - 1);
        const data = await sellerService.getSellerAnalytics(
          startDate.toISOString(),
          new Date().toISOString()
        );
        setAnalytics(data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;

    try {
      await sellerService.deleteProduct(productId);
      setProducts(products.filter((p) => p.id !== productId));
      alert('Product deleted successfully');
    } catch (err) {
      alert('Failed to delete product');
    }
  };

  return (
    <Container fluid className="py-4">
      <h1 className="mb-4">Seller Portal</h1>

      {/* Navigation Tabs */}
      <Nav variant="tabs" className="mb-4">
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'products'}
            onClick={() => setActiveTab('products')}
          >
            🏪 Products
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'orders'}
            onClick={() => setActiveTab('orders')}
          >
            📦 Orders
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link 
            active={activeTab === 'analytics'}
            onClick={() => setActiveTab('analytics')}
          >
            📊 Analytics
          </Nav.Link>
        </Nav.Item>
      </Nav>

      {/* Content */}
      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <Alert variant="danger">{error}</Alert>
      ) : (
        <>
          {activeTab === 'products' && (
            <div>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h2>My Products</h2>
                <Button variant="primary">+ Add Product</Button>
              </div>

              {products.length === 0 ? (
                <Card className="text-center p-5">
                  <Card.Body>
                    <div style={{ fontSize: '4rem' }}>📦</div>
                    <h3 className="mt-3">No Products Yet</h3>
                    <p className="text-muted">Start by adding your first product</p>
                  </Card.Body>
                </Card>
              ) : (
                <Card>
                  <Table responsive hover className="mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Product</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {products.map((product) => (
                        <tr key={product.id}>
                          <td>
                            <strong>{product.name}</strong>
                          </td>
                          <td>${product.price}</td>
                          <td>{product.quantity}</td>
                          <td>
                            {product.is_active ? (
                              <Badge bg="success">Active</Badge>
                            ) : (
                              <Badge bg="danger">Inactive</Badge>
                            )}
                          </td>
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
                      ))}
                    </tbody>
                  </Table>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'orders' && (
            <Card className="text-center p-5">
              <Card.Body>
                <h2>Order Management Coming Soon</h2>
                <p className="text-muted">View and manage orders containing your products</p>
              </Card.Body>
            </Card>
          )}

          {activeTab === 'analytics' && analytics && (
            <div>
              <h2 className="mb-4">Sales Analytics</h2>
              <Row xs={1} md={2} lg={4} className="g-4">
                <Col>
                  <Card className="text-center">
                    <Card.Body>
                      <Card.Subtitle className="mb-2 text-muted">Total Revenue</Card.Subtitle>
                      <Card.Title className="display-6">${analytics.total_revenue || 0}</Card.Title>
                    </Card.Body>
                  </Card>
                </Col>
                <Col>
                  <Card className="text-center">
                    <Card.Body>
                      <Card.Subtitle className="mb-2 text-muted">Total Orders</Card.Subtitle>
                      <Card.Title className="display-6">{analytics.total_orders || 0}</Card.Title>
                    </Card.Body>
                  </Card>
                </Col>
                <Col>
                  <Card className="text-center">
                    <Card.Body>
                      <Card.Subtitle className="mb-2 text-muted">Products Sold</Card.Subtitle>
                      <Card.Title className="display-6">{analytics.products_sold || 0}</Card.Title>
                    </Card.Body>
                  </Card>
                </Col>
                <Col>
                  <Card className="text-center">
                    <Card.Body>
                      <Card.Subtitle className="mb-2 text-muted">Avg Order Value</Card.Subtitle>
                      <Card.Title className="display-6">${analytics.average_order_value || 0}</Card.Title>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </div>
          )}
        </>
      )}
    </Container>
  );
};

export default SellerPortal;
