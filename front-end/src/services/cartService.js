import api from './api';

/**
 * Cart Service
 * Handles shopping cart operations (USER role)
 */
const cartService = {
  // Get current user's cart
  getCart: async () => {
    const response = await api.get('/cart');
    return response.data;
  },

  // Add item to cart
  addToCart: async (productId, quantity = 1, variantId = null) => {
    const response = await api.post('/cart/items', {
      product_id: productId,
      quantity,
      ...(variantId && { variant_id: variantId }),
    });
    return response.data;
  },

  // Update cart item quantity
  updateCartItem: async (itemId, quantity) => {
    const response = await api.put(`/cart/items/${itemId}`, { quantity });
    return response.data;
  },

  // Remove item from cart
  removeCartItem: async (itemId) => {
    const response = await api.delete(`/cart/items/${itemId}`);
    return response.data;
  },

  // Clear cart
  clearCart: async () => {
    const response = await api.delete('/cart');
    return response.data;
  },

  // Apply coupon
  applyCoupon: async (couponCode) => {
    const response = await api.post('/cart/coupon', { coupon_code: couponCode });
    return response.data;
  },

  // Remove coupon
  removeCoupon: async () => {
    const response = await api.delete('/cart/coupon');
    return response.data;
  },
};

export default cartService;
