import api from './api';

/**
 * Analyst Service
 * Read-only analytics, reports, data visualization (ANALYST role)
 * Routes from /api/analyst endpoint
 * ZERO write access, only aggregate data
 */
const analystService = {
  // === SYSTEM OVERVIEW ===
  
  // Get comprehensive system overview
  getSystemOverview: async () => {
    const response = await api.get('/analyst/system/overview');
    return response.data;
  },

  // === SALES ANALYTICS ===
  
  // Get sales analytics with detailed breakdown
  getSalesAnalytics: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/analyst/sales/analytics?${params}`);
    return response.data;
  },

  // === PRODUCT PERFORMANCE ===
  
  // Get product performance metrics
  getProductPerformance: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/analyst/products/performance?${params}`);
    return response.data;
  },

  // === SELLER PERFORMANCE ===
  
  // Get seller performance metrics
  getSellerPerformance: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/analyst/sellers/performance?${params}`);
    return response.data;
  },

  // === EMPLOYEE ANALYTICS ===
  
  // Get employee metrics across all departments
  getEmployeeMetrics: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/analyst/employees/metrics?${params}`);
    return response.data;
  },

  // === CUSTOMER BEHAVIOR ===
  
  // Get customer behavior analytics
  getCustomerBehavior: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/analyst/customers/behavior?${params}`);
    return response.data;
  },

  // === INVENTORY ANALYTICS ===
  
  // Get inventory turnover metrics
  getInventoryTurnover: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/analyst/inventory/turnover?${params}`);
    return response.data;
  },

  // === REVENUE TRENDS ===
  
  // Get revenue trend analysis
  getRevenueTrends: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/analyst/revenue/trends?${params}`);
    return response.data;
  },

  // === CUSTOM EXPORTS (CSV/Excel) ===
  
  // Export sales data
  exportSalesData: async (startDate, endDate, format = 'csv') => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
      format,
    });
    const response = await api.get(`/analyst/export/sales?${params}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Export product data
  exportProductData: async (format = 'csv') => {
    const params = new URLSearchParams({ format });
    const response = await api.get(`/analyst/export/products?${params}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Export customer data
  exportCustomerData: async (format = 'csv') => {
    const params = new URLSearchParams({ format });
    const response = await api.get(`/analyst/export/customers?${params}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export default analystService;
