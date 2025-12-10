import api from './api';

/**
 * Wishlist Service
 * Handles user wishlist operations
 */
const wishlistService = {
  // Get user's wishlist
  getWishlist: async () => {
    const response = await api.get('/wishlist');
    return response.data;
  },

  // Add product to wishlist
  addToWishlist: async (productId) => {
    const response = await api.post('/wishlist', { product_id: productId });
    return response.data;
  },

  // Remove from wishlist
  removeFromWishlist: async (itemId) => {
    const response = await api.delete(`/wishlist/${itemId}`);
    return response.data;
  },

  // Move wishlist item to cart
  moveToCart: async (itemId) => {
    const response = await api.post(`/wishlist/${itemId}/move-to-cart`);
    return response.data;
  },

  // Clear entire wishlist
  clearWishlist: async () => {
    const response = await api.delete('/wishlist');
    return response.data;
  },
};

export default wishlistService;
