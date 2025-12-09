import api from './api';

/**
 * Product Service
 * Handles product browsing, search, categories
 */
const productService = {
  // Get all products with pagination
  getProducts: async (params = {}) => {
    const { page = 1, limit = 20, sort = '-created_at', category = null, search = null } = params;
    const queryParams = new URLSearchParams({
      page,
      limit,
      sort,
      ...(category && { category }),
      ...(search && { search }),
    });
    const response = await api.get(`/products?${queryParams}`);
    return response.data;
  },

  // Get single product
  getProduct: async (productId) => {
    const response = await api.get(`/products/${productId}`);
    return response.data;
  },

  // Search products
  searchProducts: async (query, filters = {}) => {
    const response = await api.post('/search', { query, ...filters });
    return response.data;
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get('/catalog/categories');
    return response.data;
  },

  // Get product reviews
  getProductReviews: async (productId, page = 1) => {
    const response = await api.get(`/products/${productId}/reviews?page=${page}`);
    return response.data;
  },

  // Add product review (authenticated)
  addReview: async (productId, reviewData) => {
    const response = await api.post(`/products/${productId}/reviews`, reviewData);
    return response.data;
  },
};

export default productService;
