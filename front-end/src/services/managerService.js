import api from './api';

/**
 * Manager Service
 * Department-specific management (FINANCE_MANAGER, TRANSPORT_MANAGER, CUSTOMER_SERVICE_MANAGER)
 * ZERO cross-department access - managers only see their department
 */
const managerService = {
  // Get department employees
  getDepartmentEmployees: async (page = 1) => {
    const response = await api.get(`/manager/employees?page=${page}`);
    return response.data;
  },

  // Create employee in department
  createEmployee: async (employeeData) => {
    const response = await api.post('/manager/employees', employeeData);
    return response.data;
  },

  // Update employee in department
  updateEmployee: async (employeeId, employeeData) => {
    const response = await api.put(`/manager/employees/${employeeId}`, employeeData);
    return response.data;
  },

  // Delete employee in department
  deleteEmployee: async (employeeId) => {
    const response = await api.delete(`/manager/employees/${employeeId}`);
    return response.data;
  },

  // Get leave requests for department
  getLeaveRequests: async (page = 1, status = null) => {
    const params = new URLSearchParams({ page });
    if (status) params.append('status', status);
    const response = await api.get(`/manager/leave-requests?${params}`);
    return response.data;
  },

  // Approve/deny leave request
  processLeaveRequest: async (leaveId, action, notes = '') => {
    const response = await api.post(`/manager/leave-requests/${leaveId}/${action}`, {
      notes,
    });
    return response.data;
  },

  // Get department schedules
  getDepartmentSchedules: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/manager/schedules?${params}`);
    return response.data;
  },

  // Update employee schedule
  updateSchedule: async (employeeId, scheduleData) => {
    const response = await api.put(`/manager/schedules/${employeeId}`, scheduleData);
    return response.data;
  },

  // Approve shift swap
  approveShiftSwap: async (swapId, action) => {
    const response = await api.post(`/manager/shift-swaps/${swapId}/${action}`);
    return response.data;
  },

  // Add performance log
  addPerformanceLog: async (employeeId, logData) => {
    const response = await api.post(`/manager/employees/${employeeId}/performance`, logData);
    return response.data;
  },

  // Get performance logs
  getPerformanceLogs: async (employeeId) => {
    const response = await api.get(`/manager/employees/${employeeId}/performance`);
    return response.data;
  },

  // Get department analytics
  getDepartmentAnalytics: async (startDate, endDate) => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    const response = await api.get(`/manager/analytics?${params}`);
    return response.data;
  },

  // Override employee action (department-specific)
  overrideAction: async (actionId, overrideData) => {
    const response = await api.post(`/manager/actions/${actionId}/override`, overrideData);
    return response.data;
  },
};

export default managerService;
