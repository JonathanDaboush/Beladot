import api from './api';

/**
 * Payment Method Service
 * Handles saved payment methods for users
 */
const paymentMethodService = {
  // Get all saved payment methods
  getPaymentMethods: async () => {
    const response = await api.get('/payment-methods');
    return response.data;
  },

  // Add new payment method
  addPaymentMethod: async (paymentMethodData) => {
    const response = await api.post('/payment-methods', paymentMethodData);
    return response.data;
  },

  // Set default payment method
  setDefaultPaymentMethod: async (paymentMethodId) => {
    const response = await api.patch(`/payment-methods/${paymentMethodId}/default`);
    return response.data;
  },

  // Delete payment method
  deletePaymentMethod: async (paymentMethodId) => {
    const response = await api.delete(`/payment-methods/${paymentMethodId}`);
    return response.data;
  },
};

export default paymentMethodService;
