import api from './api';

/**
 * Transport Service
 * Handles delivery management, shipment tracking, inventory adjustments (TRANSPORT role)
 * Routes from /api/transfer endpoint
 * NO payment modifications or customer data access beyond orders
 */
const transportService = {
  // === TIME TRACKING ===
  
  // Clock in
  clockIn: async () => {
    const response = await api.post('/transfer/clock-in');
    return response.data;
  },

  // Clock out
  clockOut: async () => {
    const response = await api.post('/transfer/clock-out');
    return response.data;
  },

  // === SCHEDULE MANAGEMENT ===
  
  // Get own schedule
  getSchedule: async () => {
    const response = await api.get('/transfer/schedule');
    return response.data;
  },

  // Request leave
  requestLeave: async (leaveData) => {
    const response = await api.post('/transfer/leave/request', leaveData);
    return response.data;
  },

  // === SHIPMENT MANAGEMENT ===
  
  // Get all shipments
  getShipments: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/transfer/shipments?${params}`);
    return response.data;
  },

  // Get single shipment details
  getShipment: async (shipmentId) => {
    const response = await api.get(`/transfer/shipments/${shipmentId}`);
    return response.data;
  },

  // Update shipment status (picked, in_transit, delivered, delayed)
  updateShipmentStatus: async (shipmentId, status) => {
    const response = await api.put(`/transfer/shipments/${shipmentId}/status`, { status });
    return response.data;
  },

  // Add notes to shipment
  addShipmentNotes: async (shipmentId, notes) => {
    const response = await api.post(`/transfer/shipments/${shipmentId}/notes`, { notes });
    return response.data;
  },

  // === ORDER STATUS MANAGEMENT ===
  
  // Update order status (for logistics)
  updateOrderStatus: async (orderId, status) => {
    const response = await api.put(`/transfer/orders/${orderId}/status`, { status });
    return response.data;
  },

  // === RETURN MANAGEMENT ===
  
  // Receive return shipment (updates inventory)
  receiveReturn: async (shipmentId, returnData) => {
    const response = await api.post(`/transfer/shipments/${shipmentId}/receive`, returnData);
    return response.data;
  },

  // === INVENTORY MANAGEMENT ===
  
  // Get product inventory levels
  getProducts: async (page = 1) => {
    const response = await api.get(`/transfer/products?page=${page}`);
    return response.data;
  },

  // Adjust product stock (for returns/damages)
  adjustProductStock: async (productId, stockData) => {
    const response = await api.put(`/transfer/products/${productId}/stock`, stockData);
    return response.data;
  },

  // Import inventory
  importInventory: async (importData) => {
    const response = await api.post('/transfer/import', importData);
    return response.data;
  },

  // Export inventory
  exportInventory: async (exportData) => {
    const response = await api.post('/transfer/export', exportData);
    return response.data;
  },

  // Get inventory movements
  getInventoryMovements: async (page = 1, filters = {}) => {
    const params = new URLSearchParams({ page, ...filters });
    const response = await api.get(`/transfer/movements?${params}`);
    return response.data;
  },
};

export default transportService;
