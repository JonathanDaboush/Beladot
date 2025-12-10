import api from './api';

/**
 * Finance Service
 * Handles payroll, employee payments, financial reports (FINANCE role)
 * Routes from /api/finance, /api/payroll, /api/payroll-extended endpoints
 * NO product or transport operations allowed
 */
const financeService = {
  // === TIME TRACKING ===
  
  // Clock in
  clockIn: async () => {
    const response = await api.post('/finance/clock-in');
    return response.data;
  },

  // Clock out
  clockOut: async () => {
    const response = await api.post('/finance/clock-out');
    return response.data;
  },

  // === SCHEDULE MANAGEMENT ===
  
  // Get own schedule
  getSchedule: async () => {
    const response = await api.get('/finance/schedule');
    return response.data;
  },

  // Request leave
  requestLeave: async (leaveData) => {
    const response = await api.post('/finance/leave/request', leaveData);
    return response.data;
  },

  // === EMPLOYEE PAYROLL MANAGEMENT ===
  
  // Get all employee payroll data
  getEmployeePayrollData: async () => {
    const response = await api.get('/finance/employees/payroll');
    return response.data;
  },

  // Update employee payroll info
  updateEmployeePayroll: async (employeeId, payrollData) => {
    const response = await api.put(`/finance/employees/${employeeId}/payroll`, payrollData);
    return response.data;
  },

  // === PAYROLL PROCESSING ===
  
  // Calculate payroll for period
  calculatePayroll: async (startDate, endDate) => {
    const response = await api.post('/payroll/calculate', {
      start_date: startDate,
      end_date: endDate,
    });
    return response.data;
  },

  // Get my payroll (employee self-service)
  getMyPayroll: async () => {
    const response = await api.get('/payroll/my-payroll');
    return response.data;
  },

  // === TAX DOCUMENTS & DEDUCTIONS ===
  
  // Get tax documents
  getTaxDocuments: async (year = null) => {
    const params = year ? `?year=${year}` : '';
    const response = await api.get(`/payroll-extended/taxes${params}`);
    return response.data;
  },

  // Issue bonus
  issueBonus: async (bonusData) => {
    const response = await api.post('/payroll-extended/bonuses', bonusData);
    return response.data;
  },

  // Manage deductions
  createDeduction: async (deductionData) => {
    const response = await api.post('/payroll-extended/deductions', deductionData);
    return response.data;
  },

  updateDeduction: async (deductionId, deductionData) => {
    const response = await api.put(`/payroll-extended/deductions/${deductionId}`, deductionData);
    return response.data;
  },

  // === FINANCIAL REPORTS ===
  
  // Get revenue reports
  getRevenueReport: async (startDate, endDate) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await api.get(`/finance/reports/revenue?${params}`);
    return response.data;
  },

  // Get profit/loss statement
  getProfitLossReport: async (startDate, endDate) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await api.get(`/finance/reports/profit-loss?${params}`);
    return response.data;
  },

  // === TRANSACTION LOGS ===
  
  // Get financial transaction movements
  getFinancialMovements: async (page = 1, filters = {}) => {
    const params = new URLSearchParams({ page, ...filters });
    const response = await api.get(`/transfer/movements?${params}`);
    return response.data;
  },
};

export default financeService;
