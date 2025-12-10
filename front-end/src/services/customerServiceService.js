import api from './api';

/**
 * Customer Service Service
 * Handles CS operations - user/seller support, orders, returns, refunds (CUSTOMER_SERVICE role)
 * IMPORTANT: All actions must create audit logs (mandatory logging)
 * Routes from /api/customer-service endpoint
 */
const customerServiceService = {
  // === TIME TRACKING ===
  
  // Clock in
  clockIn: async () => {
    const response = await api.post('/customer-service/clock-in');
    return response.data;
  },

  // Clock out
  clockOut: async () => {
    const response = await api.post('/customer-service/clock-out');
    return response.data;
  },

  // === SCHEDULE MANAGEMENT ===
  
  // Get own schedule
  getSchedule: async () => {
    const response = await api.get('/customer-service/schedule');
    return response.data;
  },

  // Request leave
  requestLeave: async (leaveData) => {
    const response = await api.post('/customer-service/leave/request', leaveData);
    return response.data;
  },

  // === SELLER MANAGEMENT ===
  
  // Get all sellers
  getSellers: async () => {
    const response = await api.get('/customer-service/sellers');
    return response.data;
  },

  // Update seller (with logging)
  updateSeller: async (sellerId, data) => {
    const response = await api.put(`/customer-service/sellers/${sellerId}`, data);
    return response.data;
  },

  // === USER MANAGEMENT ===
  
  // Get all users
  getUsers: async () => {
    const response = await api.get('/customer-service/users');
    return response.data;
  },

  // Update user (with logging)
  updateUser: async (userId, data) => {
    const response = await api.put(`/customer-service/users/${userId}`, data);
    return response.data;
  },

  // === ORDER MANAGEMENT ===
  
  // Get all orders
  getOrders: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/customer-service/orders?${params}`);
    return response.data;
  },

  // Update order
  updateOrder: async (orderId, data) => {
    const response = await api.put(`/customer-service/orders/${orderId}`, data);
    return response.data;
  },

  // Process refund (with logging)
  processRefund: async (orderId, refundData) => {
    const response = await api.post(`/customer-service/orders/${orderId}/refund`, refundData);
    return response.data;
  },

  // Process return (with logging)
  processReturn: async (orderId, returnData) => {
    const response = await api.post(`/customer-service/orders/${orderId}/return`, returnData);
    return response.data;
  },

  // Create action log (mandatory for all CS actions)
  createActionLog: async (logData) => {
    const response = await api.post('/customer-service/logs', logData);
    return response.data;
  },

  // Get action logs
  getActionLogs: async (page = 1) => {
    const response = await api.get(`/customer-service/logs?page=${page}`);
    return response.data;
  },
};

export default customerServiceService;
