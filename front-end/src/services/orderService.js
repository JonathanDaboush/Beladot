import api from './api';

/**
 * Order Service
 * Handles order placement, tracking, history (USER role)
 */
const orderService = {
  // Get user's orders
  getOrders: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/orders?${params}`);
    return response.data;
  },

  // Get single order details
  getOrder: async (orderId) => {
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  },

  // Track order shipment
  trackOrder: async (orderId) => {
    const response = await api.get(`/orders/${orderId}/tracking`);
    return response.data;
  },

  // Cancel order
  cancelOrder: async (orderId, reason) => {
    const response = await api.post(`/orders/${orderId}/cancel`, { reason });
    return response.data;
  },
};

export default orderService;
