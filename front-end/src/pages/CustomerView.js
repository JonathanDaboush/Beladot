import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, InputGroup, Badge, Alert } from 'react-bootstrap';
import productService from '../services/productService';
import cartService from '../services/cartService';
import { useToast } from '../contexts/ToastContext';
import LoadingSpinner from '../components/common/LoadingSpinner';

/**
 * Customer Shopping View (Amazon/eBay style)
 * Available to: USER, SELLER, CUSTOMER_SERVICE (for testing), ADMIN
 */
const CustomerView = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [cartCount, setCartCount] = useState(0);
  const toast = useToast();

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [productsData, categoriesData, cartData] = await Promise.all([
        productService.getProducts(),
        productService.getCategories(),
        cartService.getCart().catch(() => ({ items: [] })),
      ]);
      
      setProducts(productsData.items || []);
      setCategories(categoriesData || []);
      setCartCount(cartData.items?.length || 0);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load products');
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      const data = await productService.searchProducts(searchQuery);
      setProducts(data.items || []);
    } catch (err) {
      toast.error('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryFilter = async (categoryId) => {
    setSelectedCategory(categoryId);
    try {
      setLoading(true);
      const data = await productService.getProducts({ category: categoryId });
      setProducts(data.items || []);
    } catch (err) {
      toast.error('Failed to filter products');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async (productId) => {
    try {
      await cartService.addToCart(productId, 1);
      setCartCount((prev) => prev + 1);
      toast.success('Added to cart!');
    } catch (err) {
      toast.error('Failed to add to cart');
    }
  };

  if (loading && products.length === 0) {
    return <LoadingSpinner fullScreen={true} />;
  }

  return (
    <div>
      {/* Top Navigation Bar */}
      <div className="bg-light border-bottom py-3 mb-3">
        <Container>
          <Row className="align-items-center">
            <Col md={8}>
              <Form onSubmit={handleSearch}>
                <InputGroup>
                  <Form.Control
                    type="text"
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <Button variant="primary" type="submit">
                    🔍 Search
                  </Button>
                </InputGroup>
              </Form>
            </Col>
            <Col md={4} className="text-end">
              <Button variant="outline-primary" onClick={() => alert('Cart coming soon!')}>
                🛒 Cart ({cartCount})
              </Button>
            </Col>
          </Row>
        </Container>
      </div>

      {/* Categories Bar */}
      <div className="bg-white border-bottom py-2 mb-4">
        <Container>
          <div className="d-flex gap-2 overflow-auto">
            <Button
              variant={!selectedCategory ? 'primary' : 'outline-secondary'}
              size="sm"
              onClick={() => {
                setSelectedCategory(null);
                loadInitialData();
              }}
            >
              All Products
            </Button>
            {categories.map((cat) => (
              <Button
                key={cat.id}
                variant={selectedCategory === cat.id ? 'primary' : 'outline-secondary'}
                size="sm"
                onClick={() => handleCategoryFilter(cat.id)}
              >
                {cat.name}
              </Button>
            ))}
          </div>
        </Container>
      </div>

      {/* Main Content */}
      <Container className="pb-5">
        {error && <Alert variant="danger">{error}</Alert>}

        {products.length === 0 ? (
          <div className="text-center py-5">
            <div style={{ fontSize: '4rem' }}>📦</div>
            <h2 className="mt-3">No Products Found</h2>
            <p className="text-muted">Try adjusting your search or filters</p>
          </div>
        ) : (
          <Row xs={1} sm={2} md={3} lg={4} className="g-4">
            {products.map((product) => (
              <Col key={product.id}>
                <Card className="h-100 shadow-sm">
                  <div 
                    className="bg-light d-flex align-items-center justify-content-center"
                    style={{ height: '200px' }}
                  >
                    {product.image_url ? (
                      <Card.Img 
                        variant="top" 
                        src={product.image_url} 
                        alt={product.name}
                        style={{ height: '200px', objectFit: 'cover' }}
                      />
                    ) : (
                      <div style={{ fontSize: '4rem' }}>📦</div>
                    )}
                  </div>
                  <Card.Body className="d-flex flex-column">
                    <Card.Title className="text-truncate" title={product.name}>
                      {product.name}
                    </Card.Title>
                    <div className="mb-2">
                      <strong className="text-primary fs-5">${product.price}</strong>
                    </div>
                    <div className="mb-2">
                      {product.quantity > 0 ? (
                        <Badge bg="success">In Stock</Badge>
                      ) : (
                        <Badge bg="danger">Out of Stock</Badge>
                      )}
                    </div>
                    <Card.Text 
                      className="text-muted small"
                      style={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical'
                      }}
                    >
                      {product.description}
                    </Card.Text>
                    <Button
                      variant="primary"
                      className="mt-auto w-100"
                      onClick={() => handleAddToCart(product.id)}
                      disabled={product.quantity === 0}
                    >
                      Add to Cart
                    </Button>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Container>
    </div>
  );
};

export default CustomerView;
