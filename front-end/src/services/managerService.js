import api from './api';

/**
 * Manager Service
 * Department-specific management (FINANCE_MANAGER, TRANSPORT_MANAGER, CUSTOMER_SERVICE_MANAGER)
 * Routes from /api/manager and /api/manager-approvals endpoints
 * ZERO cross-department access - managers only see their department
 */
const managerService = {
  // === EMPLOYEE MANAGEMENT (Department-Scoped) ===
  
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

  // === TIME TRACKING APPROVALS ===
  
  // Get pending time entries for approval
  getPendingTimeEntries: async () => {
    const response = await api.get('/manager/time-tracking/pending');
    return response.data;
  },

  // Approve time entry
  approveTimeEntry: async (entryId, approvalData = {}) => {
    const response = await api.put(`/manager/time-tracking/${entryId}/approve`, approvalData);
    return response.data;
  },

  // Reject time entry
  rejectTimeEntry: async (entryId, reason) => {
    const response = await api.put(`/manager/time-tracking/${entryId}/reject`, { reason });
    return response.data;
  },

  // === LEAVE REQUEST APPROVALS ===
  
  // Get pending leave requests
  getPendingLeaveRequests: async () => {
    const response = await api.get('/manager/leave/pending');
    return response.data;
  },

  // Approve leave request
  approveLeaveRequest: async (requestId, approvalData = {}) => {
    const response = await api.put(`/manager/leave/${requestId}/approve`, approvalData);
    return response.data;
  },

  // Deny leave request
  denyLeaveRequest: async (requestId, reason) => {
    const response = await api.put(`/manager/leave/${requestId}/deny`, { reason });
    return response.data;
  },

  // === SCHEDULE MANAGEMENT ===
  
  // Get department schedule
  getDepartmentSchedule: async (startDate, endDate) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await api.get(`/manager/schedule/department?${params}`);
    return response.data;
  },

  // Modify employee schedule
  modifyEmployeeSchedule: async (employeeId, scheduleData) => {
    const response = await api.put(`/manager/schedule/employee/${employeeId}`, scheduleData);
    return response.data;
  },

  // === PERFORMANCE MANAGEMENT ===
  
  // Add performance note for employee
  addPerformanceNote: async (employeeId, noteData) => {
    const response = await api.post(`/manager/performance/employee/${employeeId}`, noteData);
    return response.data;
  },

  // Get employee performance history
  getEmployeePerformance: async (employeeId) => {
    const response = await api.get(`/manager/performance/employee/${employeeId}`);
    return response.data;
  },

  // === BATCH APPROVALS (from manager_approvals router) ===
  
  // Get all pending approvals
  getAllPendingApprovals: async () => {
    const response = await api.get('/manager-approvals/pending');
    return response.data;
  },

  // Bulk approve items
  bulkApprove: async (approvalData) => {
    const response = await api.post('/manager-approvals/bulk-approve', approvalData);
    return response.data;
  },

  // Bulk deny items
  bulkDeny: async (denyData) => {
    const response = await api.post('/manager-approvals/bulk-deny', denyData);
    return response.data;
  },
};

export default managerService;
