import api from './api';

/**
 * Seller Service
 * Handles seller portal operations (SELLER role)
 */
const sellerService = {
  // Register as seller
  registerSeller: async (businessInfo, financeInfo) => {
    const response = await api.post('/seller/register', { business_info: businessInfo, finance_info: financeInfo });
    return response.data;
  },

  // Get seller profile/info
  getSellerInfo: async () => {
    const response = await api.get('/seller/my-seller-info');
    return response.data;
  },

  // Get sales report
  getSalesReport: async (params = {}) => {
    const response = await api.get('/seller/sales', { params });
    return response.data;
  },

  // Get seller products
  getSellerProducts: async (page = 1) => {
    const response = await api.get(`/seller/products?page=${page}`);
    return response.data;
  },

  // Update product (seller can only update their own)
  updateProduct: async (productId, productData) => {
    const response = await api.patch(`/seller/products/${productId}`, productData);
    return response.data;
  },

  // Update product stock
  updateProductStock: async (productId, stockData) => {
    const response = await api.patch(`/seller/products/${productId}/stock`, stockData);
    return response.data;
  },

  // Get seller performance metrics
  getPerformanceMetrics: async () => {
    const response = await api.get('/analytics/seller/performance');
    return response.data;
  },

  // Get seller finance info (Admin access)
  getSellerFinance: async (sellerId) => {
    const response = await api.get(`/seller/finance/${sellerId}`);
    return response.data;
  },
};

export default sellerService;
