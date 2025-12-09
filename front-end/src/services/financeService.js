import api from './api';

/**
 * Finance Service
 * Handles payroll, employee payments, financial reports (FINANCE role)
 * NO product or transport operations allowed
 */
const financeService = {
  // Get payroll summary
  getPayrollSummary: async (startDate, endDate) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await api.get(`/payroll/summary?${params}`);
    return response.data;
  },

  // Get employee payroll details
  getEmployeePayroll: async (employeeId, period) => {
    const response = await api.get(`/payroll/employee/${employeeId}?period=${period}`);
    return response.data;
  },

  // Create payroll run
  createPayroll: async (payrollData) => {
    const response = await api.post('/payroll', payrollData);
    return response.data;
  },

  // Update employee payment info
  updateEmployeePayment: async (employeeId, paymentData) => {
    const response = await api.put(`/finance/employee/${employeeId}/payment`, paymentData);
    return response.data;
  },

  // Get financial reports
  getFinancialReports: async (reportType, startDate, endDate) => {
    const params = new URLSearchParams({
      type: reportType,
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/finance/reports?${params}`);
    return response.data;
  },

  // Get seller payouts
  getSellerPayouts: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/transfer/payouts?${params}`);
    return response.data;
  },

  // Process seller payout
  processPayout: async (payoutId, action) => {
    const response = await api.post(`/transfer/payouts/${payoutId}/${action}`);
    return response.data;
  },

  // Generate invoice
  generateInvoice: async (invoiceData) => {
    const response = await api.post('/finance/invoices', invoiceData);
    return response.data;
  },

  // Get tax documents
  getTaxDocuments: async (year) => {
    const response = await api.get(`/finance/tax-documents?year=${year}`);
    return response.data;
  },
};

export default financeService;
