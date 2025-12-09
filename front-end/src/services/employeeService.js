import api from './api';

/**
 * Employee Service
 * Handles employee operations - clock in/out, leave requests (ALL EMPLOYEE roles)
 */
const employeeService = {
  // Get employee profile
  getEmployeeProfile: async () => {
    const response = await api.get('/employee/profile');
    return response.data;
  },

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

  // Get schedule
  getSchedule: async (startDate, endDate) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await api.get(`/scheduling?${params}`);
    return response.data;
  },

  // Request leave (sick/PTO)
  requestLeave: async (leaveData) => {
    const response = await api.post('/leave', leaveData);
    return response.data;
  },

  // Get leave requests
  getLeaveRequests: async () => {
    const response = await api.get('/leave/my-requests');
    return response.data;
  },

  // Get hours worked
  getHoursWorked: async (startDate, endDate) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    const response = await api.get(`/employee/hours?${params}`);
    return response.data;
  },
};

export default employeeService;
