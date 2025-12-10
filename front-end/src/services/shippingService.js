import api from './api';

/**
 * Shipping Service
 * Handles shipping rates and tracking
 */
const shippingService = {
  // Get shipping rate estimates
  getShippingRates: async (params) => {
    const { destination_zip, weight, dimensions } = params;
    const queryParams = new URLSearchParams({
      destination_zip,
      weight,
      ...(dimensions && { dimensions: JSON.stringify(dimensions) }),
    });
    const response = await api.get(`/shipping/rates?${queryParams}`);
    return response.data;
  },

  // Track shipment by tracking number
  trackShipment: async (trackingNumber) => {
    const response = await api.get(`/shipping/track/${trackingNumber}`);
    return response.data;
  },
};

export default shippingService;
