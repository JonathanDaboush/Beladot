import api from './api';

/**
 * Seller Service
 * Handles seller portal operations (SELLER role)
 */
const sellerService = {
  // Get seller profile
  getSellerProfile: async () => {
    const response = await api.get('/seller/profile');
    return response.data;
  },

  // Update seller profile
  updateSellerProfile: async (profileData) => {
    const response = await api.put('/seller/profile', profileData);
    return response.data;
  },

  // Get seller products
  getSellerProducts: async (page = 1) => {
    const response = await api.get(`/seller/products?page=${page}`);
    return response.data;
  },

  // Create product
  createProduct: async (productData) => {
    const response = await api.post('/products', productData);
    return response.data;
  },

  // Update product
  updateProduct: async (productId, productData) => {
    const response = await api.put(`/products/${productId}`, productData);
    return response.data;
  },

  // Delete product
  deleteProduct: async (productId) => {
    const response = await api.delete(`/products/${productId}`);
    return response.data;
  },

  // Update product inventory
  updateInventory: async (productId, quantity) => {
    const response = await api.put(`/products/${productId}/inventory`, { quantity });
    return response.data;
  },

  // Get seller orders
  getSellerOrders: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/seller/orders?${params}`);
    return response.data;
  },

  // Get seller analytics
  getSellerAnalytics: async (startDate, endDate) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await api.get(`/seller/analytics?${params}`);
    return response.data;
  },

  // Get sales report
  getSalesReport: async (period = 'month') => {
    const response = await api.get(`/seller/sales?period=${period}`);
    return response.data;
  },
};

export default sellerService;
