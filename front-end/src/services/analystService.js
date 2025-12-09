import api from './api';

/**
 * Analyst Service
 * Read-only analytics, reports, data visualization (ANALYST role)
 * ZERO write access, only aggregate data
 */
const analystService = {
  // Get business metrics
  getBusinessMetrics: async (period = 'month') => {
    const response = await api.get(`/analytics/metrics?period=${period}`);
    return response.data;
  },

  // Get sales analytics
  getSalesAnalytics: async (startDate, endDate, groupBy = 'day') => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
      group_by: groupBy,
    });
    const response = await api.get(`/analytics/sales?${params}`);
    return response.data;
  },

  // Get product analytics
  getProductAnalytics: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await api.get(`/analytics/products?${params}`);
    return response.data;
  },

  // Get customer analytics
  getCustomerAnalytics: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await api.get(`/analytics/customers?${params}`);
    return response.data;
  },

  // Get revenue reports
  getRevenueReport: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/analytics/revenue?${params}`);
    return response.data;
  },

  // Generate custom report
  generateCustomReport: async (reportConfig) => {
    const response = await api.post('/analyst/reports', reportConfig);
    return response.data;
  },

  // Export data to CSV
  exportData: async (dataType, filters = {}) => {
    const params = new URLSearchParams({ type: dataType, ...filters });
    const response = await api.get(`/analyst/export?${params}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Get dashboard KPIs
  getDashboardKPIs: async () => {
    const response = await api.get('/analytics/kpis');
    return response.data;
  },

  // Get trend analysis
  getTrendAnalysis: async (metric, period) => {
    const params = new URLSearchParams({ metric, period });
    const response = await api.get(`/analytics/trends?${params}`);
    return response.data;
  },
};

export default analystService;
