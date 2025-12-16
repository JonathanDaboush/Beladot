import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Form, Alert, Spinner } from 'react-bootstrap';
import { useCart } from '../contexts/CartContext';
import cartService from '../services/cartService';

const Cart = () => {
  const { cartItems, setCartItems, cartTotal, updateCartItemQuantity, removeFromCart, clearCart } = useCart();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      setLoading(true);
      const response = await cartService.getCart();
      setCartItems(response.data.items || []);
      setError('');
    } catch (err) {
      setError('Error loading cart. Please try again.');
      console.error('Cart fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleIncrement = async (itemId, currentQuantity) => {
    try {
      await updateCartItemQuantity(itemId, currentQuantity + 1);
      await fetchCart();
    } catch (err) {
      setError('Failed to update quantity');
    }
  };

  const handleDecrement = async (itemId, currentQuantity) => {
    if (currentQuantity > 1) {
      try {
        await updateCartItemQuantity(itemId, currentQuantity - 1);
        await fetchCart();
      } catch (err) {
        setError('Failed to update quantity');
      }
    }
  };

  const handleRemove = async (itemId) => {
    if (window.confirm('Are you sure you want to remove this item from your cart?')) {
      try {
        await removeFromCart(itemId);
        await fetchCart();
      } catch (err) {
        setError('Failed to remove item');
      }
    }
  };

  const handleClearCart = async () => {
    if (window.confirm('Are you sure you want to clear your entire cart?')) {
      try {
        await clearCart();
        setCartItems([]);
      } catch (err) {
        setError('Failed to clear cart');
      }
    }
  };

  const formatPrice = (priceCents) => {
    return `$${(priceCents / 100).toFixed(2)}`;
  };

  const calculateSubtotal = (item) => {
    return item.price_cents * item.quantity;
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => total + calculateSubtotal(item), 0);
  };

  if (loading) {
    return (
      <Container className="mt-5 text-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-3">Loading your cart...</p>
      </Container>
    );
  }

  if (cartItems.length === 0) {
    return (
      <Container className="mt-5">
        <Card className="text-center p-5">
          <Card.Body>
            <i className="bi bi-cart-x" style={{ fontSize: '4rem', color: '#6c757d' }}></i>
            <h2 className="mt-3">Your cart is empty</h2>
            <p className="text-muted">Add some products to get started!</p>
            <Button as={Link} to="/products" variant="primary" className="mt-3">
              Continue Shopping
            </Button>
          </Card.Body>
        </Card>
      </Container>
    );
  }

  return (
    <Container className="mt-5 mb-5">
      <h1 className="mb-4">Shopping Cart</h1>
      
      {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}
      
      <Row>
        <Col lg={8}>
          {cartItems.map((item) => (
            <Card key={item.id} className="mb-3 shadow-sm">
              <Card.Body>
                <Row className="align-items-center">
                  <Col md={2}>
                    <img 
                      src={item.image_url || '/placeholder.jpg'} 
                      alt={item.product_name}
                      className="img-fluid rounded"
                      style={{ maxHeight: '100px', objectFit: 'cover' }}
                    />
                  </Col>
                  <Col md={4}>
                    <h5>{item.product_name}</h5>
                    <p className="text-muted mb-0">{formatPrice(item.price_cents)} each</p>
                  </Col>
                  <Col md={3}>
                    <div className="d-flex align-items-center justify-content-center">
                      <Button 
                        variant="outline-secondary" 
                        size="sm" 
                        onClick={() => handleDecrement(item.id, item.quantity)}
                        disabled={item.quantity <= 1}
                      >
                        -
                      </Button>
                      <Form.Control 
                        type="text" 
                        value={item.quantity} 
                        readOnly 
                        className="text-center mx-2" 
                        style={{ width: '60px' }}
                      />
                      <Button 
                        variant="outline-secondary" 
                        size="sm" 
                        onClick={() => handleIncrement(item.id, item.quantity)}
                      >
                        +
                      </Button>
                    </div>
                  </Col>
                  <Col md={2} className="text-end">
                    <h5 className="mb-0">{formatPrice(calculateSubtotal(item))}</h5>
                  </Col>
                  <Col md={1} className="text-end">
                    <Button 
                      variant="outline-danger" 
                      size="sm" 
                      onClick={() => handleRemove(item.id)}
                    >
                      Remove
                    </Button>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          ))}
          
          <Button variant="outline-danger" onClick={handleClearCart}>
            Clear Cart
          </Button>
        </Col>
        
        <Col lg={4}>
          <Card className="shadow-sm sticky-top" style={{ top: '20px' }}>
            <Card.Header>
              <h4 className="mb-0">Order Summary</h4>
            </Card.Header>
            <Card.Body>
              <div className="d-flex justify-content-between mb-2">
                <span>Subtotal:</span>
                <span>{formatPrice(calculateTotal())}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Shipping:</span>
                <span>Calculated at checkout</span>
              </div>
              <hr />
              <div className="d-flex justify-content-between mb-3">
                <strong>Total:</strong>
                <strong className="text-primary">{formatPrice(calculateTotal())}</strong>
              </div>
              <Button 
                as={Link} 
                to="/checkout" 
                variant="primary" 
                size="lg" 
                className="w-100"
              >
                Proceed to Checkout
              </Button>
              <Button 
                as={Link} 
                to="/products" 
                variant="outline-secondary" 
                size="sm" 
                className="w-100 mt-2"
              >
                Continue Shopping
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Cart;
