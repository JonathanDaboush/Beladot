import api from './api';

/**
 * Transport Service
 * Handles delivery management, shipment tracking (TRANSPORT role)
 * NO payment or product modification operations allowed
 */
const transportService = {
  // Get shipments
  getShipments: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/fulfillment/shipments?${params}`);
    return response.data;
  },

  // Get single shipment
  getShipment: async (shipmentId) => {
    const response = await api.get(`/fulfillment/shipments/${shipmentId}`);
    return response.data;
  },

  // Update shipment status
  updateShipmentStatus: async (shipmentId, status, notes = '') => {
    const response = await api.put(`/fulfillment/shipments/${shipmentId}/status`, {
      status,
      notes,
    });
    return response.data;
  },

  // Get orders for fulfillment
  getOrdersForFulfillment: async (page = 1) => {
    const response = await api.get(`/fulfillment/orders?page=${page}`);
    return response.data;
  },

  // Create shipment for order
  createShipment: async (orderId, shipmentData) => {
    const response = await api.post('/fulfillment/shipments', {
      order_id: orderId,
      ...shipmentData,
    });
    return response.data;
  },

  // Handle return shipment
  processReturn: async (returnId, action, notes = '') => {
    const response = await api.post(`/fulfillment/returns/${returnId}/${action}`, {
      notes,
    });
    return response.data;
  },

  // Get return items
  getReturns: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/fulfillment/returns?${params}`);
    return response.data;
  },

  // Update return inventory (returned items)
  updateReturnInventory: async (returnId, action) => {
    // action: 'restock' or 'dispose'
    const response = await api.post(`/fulfillment/returns/${returnId}/inventory`, {
      action,
    });
    return response.data;
  },

  // Get shipping carriers
  getCarriers: async () => {
    const response = await api.get('/shipping/carriers');
    return response.data;
  },

  // Generate shipping label
  generateLabel: async (shipmentId) => {
    const response = await api.post(`/fulfillment/shipments/${shipmentId}/label`);
    return response.data;
  },

  // Track shipment
  trackShipment: async (trackingNumber) => {
    const response = await api.get(`/shipping/track/${trackingNumber}`);
    return response.data;
  },
};

export default transportService;
