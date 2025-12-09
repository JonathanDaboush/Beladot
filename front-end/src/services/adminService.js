import api from './api';

/**
 * Admin Service
 * Full system access - user management, system config, ALL operations (ADMIN role)
 */
const adminService = {
  // User Management
  getAllUsers: async (page = 1, role = null, search = null) => {
    const params = new URLSearchParams({ page });
    if (role) params.append('role', role);
    if (search) params.append('search', search);
    const response = await api.get(`/admin/users?${params}`);
    return response.data;
  },

  createUser: async (userData) => {
    const response = await api.post('/admin/users', userData);
    return response.data;
  },

  updateUser: async (userId, userData) => {
    const response = await api.put(`/admin/users/${userId}`, userData);
    return response.data;
  },

  deleteUser: async (userId) => {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  },

  updateUserRole: async (userId, role) => {
    const response = await api.put(`/admin/users/${userId}/role`, { role });
    return response.data;
  },

  resetUserPassword: async (userId) => {
    const response = await api.post(`/admin/users/${userId}/reset-password`);
    return response.data;
  },

  // System Configuration
  getSystemConfig: async () => {
    const response = await api.get('/admin/config');
    return response.data;
  },

  updateSystemConfig: async (configData) => {
    const response = await api.put('/admin/config', configData);
    return response.data;
  },

  // Feature Flags
  getFeatureFlags: async () => {
    const response = await api.get('/admin/feature-flags');
    return response.data;
  },

  toggleFeatureFlag: async (flagName, enabled) => {
    const response = await api.put(`/admin/feature-flags/${flagName}`, { enabled });
    return response.data;
  },

  // Audit Logs
  getAuditLogs: async (page = 1, filters = {}) => {
    const params = new URLSearchParams({ page, ...filters });
    const response = await api.get(`/admin/audit-logs?${params}`);
    return response.data;
  },

  // Product Management (ALL sellers)
  getAllProducts: async (page = 1, sellerId = null) => {
    const params = new URLSearchParams({ page });
    if (sellerId) params.append('seller_id', sellerId);
    const response = await api.get(`/admin/products?${params}`);
    return response.data;
  },

  updateAnyProduct: async (productId, productData) => {
    const response = await api.put(`/admin/products/${productId}`, productData);
    return response.data;
  },

  deleteAnyProduct: async (productId) => {
    const response = await api.delete(`/admin/products/${productId}`);
    return response.data;
  },

  // Order Management (ALL orders)
  getAllOrders: async (page = 1, filters = {}) => {
    const params = new URLSearchParams({ page, ...filters });
    const response = await api.get(`/admin/orders?${params}`);
    return response.data;
  },

  updateAnyOrder: async (orderId, orderData) => {
    const response = await api.put(`/admin/orders/${orderId}`, orderData);
    return response.data;
  },

  // Payment Management
  getAllPayments: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/admin/payments?${params}`);
    return response.data;
  },

  processRefundOverride: async (refundId, action, reason) => {
    const response = await api.post(`/admin/refunds/${refundId}/${action}`, { reason });
    return response.data;
  },

  // API Key Management
  getApiKeys: async () => {
    const response = await api.get('/admin/api-keys');
    return response.data;
  },

  createApiKey: async (keyData) => {
    const response = await api.post('/admin/api-keys', keyData);
    return response.data;
  },

  revokeApiKey: async (keyId) => {
    const response = await api.delete(`/admin/api-keys/${keyId}`);
    return response.data;
  },

  // System Settings
  updateTaxRates: async (taxData) => {
    const response = await api.put('/admin/settings/tax', taxData);
    return response.data;
  },

  updateShippingRates: async (shippingData) => {
    const response = await api.put('/admin/settings/shipping', shippingData);
    return response.data;
  },

  updatePaymentGateways: async (gatewayData) => {
    const response = await api.put('/admin/settings/payment-gateways', gatewayData);
    return response.data;
  },

  // Database Maintenance
  getDatabaseStats: async () => {
    const response = await api.get('/admin/database/stats');
    return response.data;
  },

  runMaintenance: async (maintenanceType) => {
    const response = await api.post('/admin/database/maintenance', { type: maintenanceType });
    return response.data;
  },
};

export default adminService;
