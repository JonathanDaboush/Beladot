import api from './api';

/**
 * Fulfillment Service
 * Handles order fulfillment, shipment tracking, returns, and refunds
 */
const fulfillmentService = {
  // Get shipment tracking info
  trackShipment: async (shipmentId) => {
    const response = await api.get(`/shipments/${shipmentId}/track`);
    return response.data;
  },

  // Get shipments for an order
  getOrderShipments: async (orderId) => {
    const response = await api.get(`/shipments/order/${orderId}`);
    return response.data;
  },

  // Request return
  requestReturn: async (returnData) => {
    const response = await api.post('/fulfillment/returns/request', returnData);
    return response.data;
  },

  // Request refund
  requestRefund: async (refundData) => {
    const response = await api.post('/fulfillment/refunds/request', refundData);
    return response.data;
  },

  // Get return status
  getReturnStatus: async (returnId) => {
    const response = await api.get(`/fulfillment/returns/${returnId}`);
    return response.data;
  },

  // Get refund status
  getRefundStatus: async (refundId) => {
    const response = await api.get(`/fulfillment/refunds/${refundId}`);
    return response.data;
  },
};

export default fulfillmentService;
