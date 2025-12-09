import api from './api';

/**
 * Customer Service Service
 * Handles CS operations - tickets, refunds, returns, user support (CUSTOMER_SERVICE role)
 * IMPORTANT: All actions must be logged with mandatory audit trail
 */
const customerServiceService = {
  // Get all tickets
  getTickets: async (page = 1, status = null, priority = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);
    const response = await api.get(`/customer-service/tickets?${params}`);
    return response.data;
  },

  // Get single ticket
  getTicket: async (ticketId) => {
    const response = await api.get(`/customer-service/tickets/${ticketId}`);
    return response.data;
  },

  // Update ticket status
  updateTicket: async (ticketId, updateData, reason) => {
    const response = await api.put(`/customer-service/tickets/${ticketId}`, {
      ...updateData,
      action_reason: reason, // Mandatory logging
    });
    return response.data;
  },

  // Get refund requests
  getRefundRequests: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/customer-service/refunds?${params}`);
    return response.data;
  },

  // Approve/deny refund
  processRefund: async (refundId, action, reason) => {
    const response = await api.post(`/customer-service/refunds/${refundId}/${action}`, {
      reason, // Mandatory logging
    });
    return response.data;
  },

  // Get return requests
  getReturnRequests: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/customer-service/returns?${params}`);
    return response.data;
  },

  // Approve/deny return
  processReturn: async (returnId, action, reason) => {
    const response = await api.post(`/customer-service/returns/${returnId}/${action}`, {
      reason, // Mandatory logging
    });
    return response.data;
  },

  // View user details (for support)
  viewUserDetails: async (userId, reason) => {
    const response = await api.get(`/customer-service/users/${userId}?reason=${encodeURIComponent(reason)}`);
    return response.data;
  },

  // Impersonate user action (with logging)
  performUserAction: async (userId, action, actionData, reason) => {
    const response = await api.post('/customer-service/impersonate', {
      user_id: userId,
      action,
      action_data: actionData,
      reason, // Mandatory logging
    });
    return response.data;
  },

  // Get audit logs for CS actions
  getAuditLogs: async (page = 1, filters = {}) => {
    const params = new URLSearchParams({ page, ...filters });
    const response = await api.get(`/customer-service/audit-logs?${params}`);
    return response.data;
  },
};

export default customerServiceService;
