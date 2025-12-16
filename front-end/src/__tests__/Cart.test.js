import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Cart from '../pages/Cart';
import { CartProvider } from '../contexts/CartContext';
import { AuthProvider } from '../contexts/AuthContext';
import axios from 'axios';

jest.mock('axios');

describe('Cart Page Component', () => {
  const mockCartItems = [
    {
      id: '1',
      product_id: 'prod1',
      product_name: 'Wireless Headphones',
      price_cents: 7999,
      quantity: 2,
      image_url: '/images/headphones.jpg'
    },
    {
      id: '2',
      product_id: 'prod2',
      product_name: 'USB Cable',
      price_cents: 1499,
      quantity: 1,
      image_url: '/images/cable.jpg'
    }
  ];

  const renderWithProviders = (component) => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <CartProvider>
            {component}
          </CartProvider>
        </AuthProvider>
      </BrowserRouter>
    );
  };

  beforeEach(() => {
    axios.get.mockResolvedValue({
      data: { items: mockCartItems, total_cents: 17497 }
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders cart with items', async () => {
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      expect(screen.getByText('Wireless Headphones')).toBeInTheDocument();
      expect(screen.getByText('USB Cable')).toBeInTheDocument();
    });
  });

  test('displays correct total price', async () => {
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      expect(screen.getByText(/\$174\.97/)).toBeInTheDocument();
    });
  });

  test('displays empty cart message when no items', async () => {
    axios.get.mockResolvedValue({
      data: { items: [], total_cents: 0 }
    });
    
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      expect(screen.getByText(/your cart is empty/i)).toBeInTheDocument();
    });
  });

  test('updates quantity when increment button clicked', async () => {
    axios.patch.mockResolvedValue({
      data: { ...mockCartItems[0], quantity: 3 }
    });
    
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      expect(screen.getByText('Wireless Headphones')).toBeInTheDocument();
    });
    
    const incrementButtons = screen.getAllByRole('button', { name: /\+/i });
    fireEvent.click(incrementButtons[0]);
    
    await waitFor(() => {
      expect(axios.patch).toHaveBeenCalledWith(
        expect.stringContaining('/api/cart/items/1'),
        { quantity: 3 },
        expect.any(Object)
      );
    });
  });

  test('updates quantity when decrement button clicked', async () => {
    axios.patch.mockResolvedValue({
      data: { ...mockCartItems[0], quantity: 1 }
    });
    
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      expect(screen.getByText('Wireless Headphones')).toBeInTheDocument();
    });
    
    const decrementButtons = screen.getAllByRole('button', { name: /-/i });
    fireEvent.click(decrementButtons[0]);
    
    await waitFor(() => {
      expect(axios.patch).toHaveBeenCalledWith(
        expect.stringContaining('/api/cart/items/1'),
        { quantity: 1 },
        expect.any(Object)
      );
    });
  });

  test('removes item when remove button clicked', async () => {
    axios.delete.mockResolvedValue({ data: { message: 'Item removed' } });
    
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      expect(screen.getByText('Wireless Headphones')).toBeInTheDocument();
    });
    
    const removeButtons = screen.getAllByRole('button', { name: /remove/i });
    fireEvent.click(removeButtons[0]);
    
    await waitFor(() => {
      expect(axios.delete).toHaveBeenCalledWith(
        expect.stringContaining('/api/cart/items/1'),
        expect.any(Object)
      );
    });
  });

  test('navigates to checkout when checkout button clicked', async () => {
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      expect(screen.getByText('Wireless Headphones')).toBeInTheDocument();
    });
    
    const checkoutButton = screen.getByRole('button', { name: /proceed to checkout/i });
    expect(checkoutButton).toBeInTheDocument();
    expect(checkoutButton).toHaveAttribute('href', '/checkout');
  });

  test('shows loading state while fetching cart', () => {
    renderWithProviders(<Cart />);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('displays error message on fetch failure', async () => {
    axios.get.mockRejectedValue(new Error('Network error'));
    
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      expect(screen.getByText(/error loading cart/i)).toBeInTheDocument();
    });
  });

  test('calculates item subtotal correctly', async () => {
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      // Wireless Headphones: $79.99 × 2 = $159.98
      expect(screen.getByText(/\$159\.98/)).toBeInTheDocument();
      // USB Cable: $14.99 × 1 = $14.99
      expect(screen.getByText(/\$14\.99/)).toBeInTheDocument();
    });
  });

  test('prevents quantity from going below 1', async () => {
    const singleItemCart = [{
      ...mockCartItems[0],
      quantity: 1
    }];
    
    axios.get.mockResolvedValue({
      data: { items: singleItemCart, total_cents: 7999 }
    });
    
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      expect(screen.getByText('Wireless Headphones')).toBeInTheDocument();
    });
    
    const decrementButton = screen.getByRole('button', { name: /-/i });
    expect(decrementButton).toBeDisabled();
  });

  test('shows confirmation dialog before removing item', async () => {
    window.confirm = jest.fn(() => true);
    axios.delete.mockResolvedValue({ data: { message: 'Item removed' } });
    
    renderWithProviders(<Cart />);
    
    await waitFor(() => {
      expect(screen.getByText('Wireless Headphones')).toBeInTheDocument();
    });
    
    const removeButtons = screen.getAllByRole('button', { name: /remove/i });
    fireEvent.click(removeButtons[0]);
    
    expect(window.confirm).toHaveBeenCalledWith(
      expect.stringContaining('remove this item')
    );
  });
});
