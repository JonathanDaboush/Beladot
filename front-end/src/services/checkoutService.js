import api from './api';

/**
 * Checkout Service
 * Handles checkout process and payment (USER role)
 */
const checkoutService = {
  // Initiate checkout
  initiateCheckout: async (checkoutData) => {
    const response = await api.post('/checkout', checkoutData);
    return response.data;
  },

  // Calculate shipping
  calculateShipping: async (addressId, items) => {
    const response = await api.post('/checkout/shipping', { address_id: addressId, items });
    return response.data;
  },

  // Apply payment method
  processPayment: async (orderId, paymentData) => {
    const response = await api.post('/payments', {
      order_id: orderId,
      ...paymentData,
    });
    return response.data;
  },

  // Get available shipping methods
  getShippingMethods: async () => {
    const response = await api.get('/shipping/methods');
    return response.data;
  },
};

export default checkoutService;
