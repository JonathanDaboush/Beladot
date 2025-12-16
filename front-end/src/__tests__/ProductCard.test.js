import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import ProductCard from '../components/ProductCard';

describe('ProductCard Component', () => {
  const mockProduct = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    name: 'Wireless Headphones',
    description: 'High quality wireless headphones',
    price_cents: 7999,
    image_url: '/images/headphones.jpg',
    category: 'Electronics',
    rating: 4.5,
    reviews_count: 128
  };

  const renderWithRouter = (component) => {
    return render(
      <BrowserRouter>
        {component}
      </BrowserRouter>
    );
  };

  test('renders product card with correct information', () => {
    renderWithRouter(<ProductCard product={mockProduct} />);
    
    expect(screen.getByText('Wireless Headphones')).toBeInTheDocument();
    expect(screen.getByText(/\$79\.99/)).toBeInTheDocument();
    expect(screen.getByText('Electronics')).toBeInTheDocument();
  });

  test('displays product image with correct alt text', () => {
    renderWithRouter(<ProductCard product={mockProduct} />);
    
    const image = screen.getByRole('img', { name: /wireless headphones/i });
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', '/images/headphones.jpg');
  });

  test('shows rating and reviews count', () => {
    renderWithRouter(<ProductCard product={mockProduct} />);
    
    expect(screen.getByText('4.5')).toBeInTheDocument();
    expect(screen.getByText('(128 reviews)')).toBeInTheDocument();
  });

  test('calls onAddToCart when add to cart button is clicked', async () => {
    const mockAddToCart = jest.fn();
    
    renderWithRouter(
      <ProductCard product={mockProduct} onAddToCart={mockAddToCart} />
    );
    
    const addButton = screen.getByRole('button', { name: /add to cart/i });
    fireEvent.click(addButton);
    
    await waitFor(() => {
      expect(mockAddToCart).toHaveBeenCalledWith(mockProduct.id);
    });
  });

  test('navigates to product detail on card click', () => {
    renderWithRouter(<ProductCard product={mockProduct} />);
    
    const card = screen.getByTestId('product-card');
    expect(card).toHaveAttribute('href', `/products/${mockProduct.id}`);
  });

  test('displays discount badge when product is on sale', () => {
    const saleProduct = {
      ...mockProduct,
      compare_at_price_cents: 9999,
      price_cents: 7999
    };
    
    renderWithRouter(<ProductCard product={saleProduct} />);
    
    expect(screen.getByText(/20% off/i)).toBeInTheDocument();
  });

  test('shows out of stock badge when stock is zero', () => {
    const outOfStockProduct = {
      ...mockProduct,
      stock_quantity: 0
    };
    
    renderWithRouter(<ProductCard product={outOfStockProduct} />);
    
    expect(screen.getByText(/out of stock/i)).toBeInTheDocument();
    
    const addButton = screen.queryByRole('button', { name: /add to cart/i });
    expect(addButton).toBeDisabled();
  });

  test('truncates long descriptions', () => {
    const longDescProduct = {
      ...mockProduct,
      description: 'This is a very long description that should be truncated after a certain number of characters to keep the card layout clean and consistent'
    };
    
    renderWithRouter(<ProductCard product={longDescProduct} />);
    
    const description = screen.getByText(/this is a very long description/i);
    expect(description.textContent.length).toBeLessThan(longDescProduct.description.length);
  });
});
