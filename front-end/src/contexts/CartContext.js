import React, { createContext, useContext, useState, useEffect } from 'react';
import cartService from '../services/cartService';
import { useToast } from './ToastContext';

const CartContext = createContext(null);

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  // Load cart on mount
  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      setLoading(true);
      const data = await cartService.getCart();
      setCart(data);
    } catch (error) {
      console.error('Failed to load cart:', error);
      setCart({ items: [], total_cents: 0, item_count: 0 });
    } finally {
      setLoading(false);
    }
  };

  // Optimistic add to cart with rollback
  const addToCart = async (productId, quantity = 1, variantId = null) => {
    // Save previous state
    const previousCart = cart;

    try {
      // Optimistic update
      const optimisticItem = {
        product_id: productId,
        quantity,
        variant_id: variantId,
        id: Date.now(), // Temporary ID
      };

      setCart((prev) => ({
        ...prev,
        items: [...(prev?.items || []), optimisticItem],
        item_count: (prev?.item_count || 0) + quantity,
      }));

      // Make API call
      await cartService.addToCart(productId, quantity, variantId);
      
      // Reload actual cart data from server
      await loadCart();
      
      toast.success('Added to cart!');
      return true;
    } catch (error) {
      // Rollback on error
      setCart(previousCart);
      toast.error(error.response?.data?.detail || 'Failed to add to cart');
      return false;
    }
  };

  // Optimistic remove from cart with rollback
  const removeFromCart = async (productId) => {
    const previousCart = cart;

    try {
      // Optimistic update
      setCart((prev) => ({
        ...prev,
        items: prev?.items.filter((item) => item.product_id !== productId) || [],
        item_count: Math.max(0, (prev?.item_count || 0) - 1),
      }));

      // Make API call
      await cartService.removeCartItem(productId);
      
      // Reload actual cart data
      await loadCart();
      
      toast.success('Removed from cart');
      return true;
    } catch (error) {
      // Rollback on error
      setCart(previousCart);
      toast.error('Failed to remove from cart');
      return false;
    }
  };

  // Update cart item quantity with optimistic update
  const updateQuantity = async (productId, quantity) => {
    const previousCart = cart;

    try {
      // Optimistic update
      setCart((prev) => ({
        ...prev,
        items: prev?.items.map((item) =>
          item.product_id === productId ? { ...item, quantity } : item
        ) || [],
      }));

      // Make API call
      await cartService.updateCartItem(productId, quantity);
      
      // Reload actual cart data
      await loadCart();
      
      return true;
    } catch (error) {
      // Rollback on error
      setCart(previousCart);
      toast.error('Failed to update quantity');
      return false;
    }
  };

  // Clear cart
  const clearCart = async () => {
    const previousCart = cart;

    try {
      setCart({ items: [], total_cents: 0, item_count: 0 });
      await cartService.clearCart();
      toast.success('Cart cleared');
      return true;
    } catch (error) {
      setCart(previousCart);
      toast.error('Failed to clear cart');
      return false;
    }
  };

  const value = {
    cart,
    loading,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    refreshCart: loadCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};
