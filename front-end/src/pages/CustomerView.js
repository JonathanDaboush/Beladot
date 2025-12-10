import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, InputGroup, Badge, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import productService from '../services/productService';
import catalogService from '../services/catalogService';
import { useCart } from '../contexts/CartContext';
import { useToast } from '../contexts/ToastContext';
import { ProductCardSkeleton } from '../components/common/LoadingSkeleton';
import { EmptyProductsState } from '../components/common/EmptyState';
import { useKeyboardShortcuts, SHORTCUTS } from '../utils/keyboardShortcuts';
import { formatCurrency } from '../utils/formatters';

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
  const { cart, addToCart: addToCartContext } = useCart();
  const toast = useToast();
  const navigate = useNavigate();

  // Keyboard shortcuts
  const shortcuts = [
    { ...SHORTCUTS.CUSTOMER.VIEW_CART, callback: () => navigate('/cart') },
    { ...SHORTCUTS.GLOBAL.SEARCH, callback: () => document.querySelector('input[type="text"]')?.focus() },
  ];
  useKeyboardShortcuts(shortcuts, [navigate]);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [productsData, categoriesData] = await Promise.all([
        productService.getProducts(),
        catalogService.getCategories(),
      ]);
      
      setProducts(productsData.items || productsData || []);
      setCategories(categoriesData || []);
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

  const handleAddToCart = async (product) => {
    // Prevent adding out-of-stock items
    if (product.quantity === 0) {
      toast.error('This product is out of stock');
      return;
    }

    // Use CartContext for optimistic update
    await addToCartContext(product.id, 1);
  };

  const cartCount = cart?.items?.length || 0;

  if (loading && products.length === 0) {
    return (
      <Container className="py-5">
        <Row xs={1} sm={2} md={3} lg={4} className="g-4">
          {[...Array(8)].map((_, idx) => (
            <Col key={idx}>
              <ProductCardSkeleton />
            </Col>
          ))}
        </Row>
      </Container>
    );
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
              <Button variant="outline-primary" onClick={() => navigate('/cart')}>
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
          <EmptyProductsState 
            message={selectedCategory ? "No products in this category" : "No products available"}
            action={selectedCategory && (() => {
              setSelectedCategory(null);
              loadInitialData();
            })}
          />
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
                      <strong className="text-primary fs-5">{formatCurrency(product.price)}</strong>
                    </div>
                    <div className="mb-2">
                      {product.quantity > 0 ? (
                        <Badge bg="success">In Stock ({product.quantity})</Badge>
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
                      onClick={() => handleAddToCart(product)}
                      disabled={product.quantity === 0}
                    >
                      {product.quantity === 0 ? 'Out of Stock' : 'Add to Cart'}
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
