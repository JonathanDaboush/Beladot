import React from 'react';
import { Link } from 'react-router-dom';
import { Card, Button, Badge } from 'react-bootstrap';
import './ProductCard.css';

const ProductCard = ({ product, onAddToCart }) => {
  const formatPrice = (priceCents) => {
    return `$${(priceCents / 100).toFixed(2)}`;
  };

  const calculateDiscount = () => {
    if (product.compare_at_price_cents && product.compare_at_price_cents > product.price_cents) {
      const discount = ((product.compare_at_price_cents - product.price_cents) / product.compare_at_price_cents * 100).toFixed(0);
      return `${discount}% off`;
    }
    return null;
  };

  const truncateDescription = (text, maxLength = 100) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const isOutOfStock = product.stock_quantity === 0;
  const discount = calculateDiscount();

  const handleAddToCart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onAddToCart && !isOutOfStock) {
      onAddToCart(product.id);
    }
  };

  return (
    <Card 
      className="product-card h-100 shadow-sm" 
      as={Link} 
      to={`/products/${product.id}`}
      data-testid="product-card"
      style={{ textDecoration: 'none', color: 'inherit' }}
    >
      <div className="position-relative">
        <Card.Img 
          variant="top" 
          src={product.image_url || '/placeholder.jpg'} 
          alt={product.name}
          style={{ height: '200px', objectFit: 'cover' }}
        />
        {discount && (
          <Badge bg="danger" className="position-absolute top-0 end-0 m-2">
            {discount}
          </Badge>
        )}
        {isOutOfStock && (
          <Badge bg="secondary" className="position-absolute top-0 start-0 m-2">
            Out of Stock
          </Badge>
        )}
      </div>
      
      <Card.Body className="d-flex flex-column">
        <Card.Title className="text-truncate">{product.name}</Card.Title>
        <Card.Text className="text-muted small">{product.category}</Card.Text>
        <Card.Text className="text-muted small flex-grow-1">
          {truncateDescription(product.description)}
        </Card.Text>
        
        <div className="mt-auto">
          <div className="d-flex align-items-center justify-content-between mb-2">
            <div>
              <h5 className="mb-0 text-primary">{formatPrice(product.price_cents)}</h5>
              {product.compare_at_price_cents && (
                <small className="text-muted text-decoration-line-through">
                  {formatPrice(product.compare_at_price_cents)}
                </small>
              )}
            </div>
            {product.rating && (
              <div className="text-warning">
                <i className="bi bi-star-fill"></i> {product.rating}
                {product.reviews_count && (
                  <small className="text-muted"> ({product.reviews_count} reviews)</small>
                )}
              </div>
            )}
          </div>
          
          <Button 
            variant={isOutOfStock ? "secondary" : "primary"}
            size="sm" 
            className="w-100"
            onClick={handleAddToCart}
            disabled={isOutOfStock}
          >
            {isOutOfStock ? 'Out of Stock' : 'Add to Cart'}
          </Button>
        </div>
      </Card.Body>
    </Card>
  );
};

export default ProductCard;
