import api from './api';

/**
 * Employee Service
 * Handles employee operations - clock in/out, leave requests, schedule (ALL EMPLOYEE roles)
 * Routes from /api/employee endpoint
 */
const employeeService = {
  // === TIME TRACKING ===
  
  // Clock in
  clockIn: async () => {
    const response = await api.post('/employee/clock-in');
    return response.data;
  },

  // Clock out
  clockOut: async () => {
    const response = await api.post('/employee/clock-out');
    return response.data;
  },

  // Get my hours worked
  getMyHours: async (startDate, endDate) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await api.get(`/employee/hours?${params}`);
    return response.data;
  },

  // === SCHEDULING ===
  
  // Get my schedule
  getMySchedule: async (startDate, endDate) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await api.get(`/employee/schedule?${params}`);
    return response.data;
  },

  // Request schedule change
  requestScheduleChange: async (scheduleData) => {
    const response = await api.post('/employee/schedule/change-request', scheduleData);
    return response.data;
  },

  // Get who is working
  getWhoIsWorking: async (targetDate, startTime = null, endTime = null) => {
    const params = new URLSearchParams({ target_date: targetDate });
    if (startTime) params.append('start_time', startTime);
    if (endTime) params.append('end_time', endTime);
    const response = await api.get(`/employee/shifts/who-working?${params}`);
    return response.data;
  },

  // Apply for shift
  applyForShift: async (shiftDate, shiftStart, shiftEnd, reason = null) => {
    const response = await api.post('/employee/shifts/apply', {
      shift_date: shiftDate,
      shift_start: shiftStart,
      shift_end: shiftEnd,
      reason,
    });
    return response.data;
  },

  // Check coverage status
  checkCoverageStatus: async (date, department = null) => {
    const params = new URLSearchParams({ date });
    if (department) params.append('department', department);
    const response = await api.get(`/employee/shifts/coverage-status?${params}`);
    return response.data;
  },

  // === LEAVE MANAGEMENT ===
  
  // Request leave (PTO/sick)
  requestLeave: async (leaveData) => {
    const response = await api.post('/employee/leave/request', leaveData);
    return response.data;
  },

  // Get my leave requests
  getMyLeaveRequests: async () => {
    const response = await api.get('/employee/leave/my-requests');
    return response.data;
  },

  // Cancel leave request
  cancelLeaveRequest: async (requestId) => {
    const response = await api.delete(`/employee/leave/${requestId}`);
    return response.data;
  },

  // Get leave balance
  getLeaveBalance: async () => {
    const response = await api.get('/employee/leave/balance');
    return response.data;
  },

  // === PROFILE ===
  
  // Get employee profile
  getProfile: async () => {
    const response = await api.get('/employee/profile');
    return response.data;
  },

  // Update employee profile
  updateProfile: async (profileData) => {
    const response = await api.put('/employee/profile', profileData);
    return response.data;
  },
};

export default employeeService;
