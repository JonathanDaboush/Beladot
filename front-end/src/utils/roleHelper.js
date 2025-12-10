/**
 * Role Helper Utilities
 * Centralized role checking and permission logic
 */

export const USER_ROLES = {
  CUSTOMER: 'CUSTOMER',
  SELLER: 'SELLER',
  EMPLOYEE: 'EMPLOYEE',
  CUSTOMER_SERVICE: 'CUSTOMER_SERVICE',
  FINANCE: 'FINANCE',
  TRANSPORT: 'TRANSPORT',
  CUSTOMER_SERVICE_MANAGER: 'CUSTOMER_SERVICE_MANAGER',
  FINANCE_MANAGER: 'FINANCE_MANAGER',
  TRANSPORT_MANAGER: 'TRANSPORT_MANAGER',
  ANALYST: 'ANALYST',
  ADMIN: 'ADMIN',
};

// Role groups for easier checking
export const ROLE_GROUPS = {
  CUSTOMERS: [USER_ROLES.CUSTOMER],
  SELLERS: [USER_ROLES.SELLER],
  EMPLOYEES: [USER_ROLES.EMPLOYEE],
  CS_TEAM: [USER_ROLES.CUSTOMER_SERVICE, USER_ROLES.CUSTOMER_SERVICE_MANAGER],
  FINANCE_TEAM: [USER_ROLES.FINANCE, USER_ROLES.FINANCE_MANAGER],
  TRANSPORT_TEAM: [USER_ROLES.TRANSPORT, USER_ROLES.TRANSPORT_MANAGER],
  ALL_MANAGERS: [
    USER_ROLES.CUSTOMER_SERVICE_MANAGER,
    USER_ROLES.FINANCE_MANAGER,
    USER_ROLES.TRANSPORT_MANAGER,
  ],
  ANALYSTS: [USER_ROLES.ANALYST],
  ADMINS: [USER_ROLES.ADMIN],
};

// Check if user is in a specific role
export const isRole = (userRole, targetRole) => {
  return userRole === targetRole;
};

// Check if user is in any of the given roles
export const hasAnyRole = (userRole, allowedRoles) => {
  return allowedRoles.includes(userRole);
};

// Check if user is a customer
export const isCustomer = (role) => {
  return role === USER_ROLES.CUSTOMER;
};

// Check if user is a seller
export const isSeller = (role) => {
  return role === USER_ROLES.SELLER;
};

// Check if user is any kind of employee
export const isEmployee = (role) => {
  return [
    USER_ROLES.EMPLOYEE,
    USER_ROLES.CUSTOMER_SERVICE,
    USER_ROLES.FINANCE,
    USER_ROLES.TRANSPORT,
  ].includes(role);
};

// Check if user is a manager (any department)
export const isManager = (role) => {
  return ROLE_GROUPS.ALL_MANAGERS.includes(role);
};

// Check if user is an analyst
export const isAnalyst = (role) => {
  return role === USER_ROLES.ANALYST;
};

// Check if user is an admin
export const isAdmin = (role) => {
  return role === USER_ROLES.ADMIN;
};

// Check if user has write permissions (not analyst)
export const hasWritePermissions = (role) => {
  return role !== USER_ROLES.ANALYST;
};

// Get department from role
export const getDepartment = (role) => {
  if (ROLE_GROUPS.CS_TEAM.includes(role)) return 'CUSTOMER_SERVICE';
  if (ROLE_GROUPS.FINANCE_TEAM.includes(role)) return 'FINANCE';
  if (ROLE_GROUPS.TRANSPORT_TEAM.includes(role)) return 'TRANSPORT';
  return null;
};

// Get role display name
export const getRoleDisplayName = (role) => {
  const displayNames = {
    [USER_ROLES.CUSTOMER]: 'Customer',
    [USER_ROLES.SELLER]: 'Seller',
    [USER_ROLES.EMPLOYEE]: 'Employee',
    [USER_ROLES.CUSTOMER_SERVICE]: 'Customer Service',
    [USER_ROLES.FINANCE]: 'Finance',
    [USER_ROLES.TRANSPORT]: 'Transport',
    [USER_ROLES.CUSTOMER_SERVICE_MANAGER]: 'CS Manager',
    [USER_ROLES.FINANCE_MANAGER]: 'Finance Manager',
    [USER_ROLES.TRANSPORT_MANAGER]: 'Transport Manager',
    [USER_ROLES.ANALYST]: 'Analyst',
    [USER_ROLES.ADMIN]: 'Admin',
  };
  return displayNames[role] || role;
};

// Get role badge color for UI
export const getRoleBadgeColor = (role) => {
  if (isAdmin(role)) return 'danger';
  if (isAnalyst(role)) return 'info';
  if (isManager(role)) return 'warning';
  if (isEmployee(role)) return 'secondary';
  if (isSeller(role)) return 'success';
  if (isCustomer(role)) return 'primary';
  return 'secondary';
};

// Check if user can view sensitive data
export const canViewSensitiveData = (role) => {
  return [
    USER_ROLES.FINANCE,
    USER_ROLES.FINANCE_MANAGER,
    USER_ROLES.ADMIN,
  ].includes(role);
};

// Check if user can manage employees
export const canManageEmployees = (role) => {
  return isManager(role) || isAdmin(role);
};

// Check if user can view analytics
export const canViewAnalytics = (role) => {
  return [
    USER_ROLES.ANALYST,
    USER_ROLES.ADMIN,
    ...ROLE_GROUPS.ALL_MANAGERS,
  ].includes(role);
};

// Check if user can approve time entries
export const canApproveTimeEntries = (role) => {
  return isManager(role) || isAdmin(role);
};

// Check if user can process refunds
export const canProcessRefunds = (role) => {
  return [
    USER_ROLES.CUSTOMER_SERVICE,
    USER_ROLES.CUSTOMER_SERVICE_MANAGER,
    USER_ROLES.FINANCE,
    USER_ROLES.FINANCE_MANAGER,
    USER_ROLES.ADMIN,
  ].includes(role);
};

// Check if user can manage inventory
export const canManageInventory = (role) => {
  return [
    USER_ROLES.TRANSPORT,
    USER_ROLES.TRANSPORT_MANAGER,
    USER_ROLES.ADMIN,
  ].includes(role);
};

// Get default route for role
export const getDefaultRoute = (role) => {
  if (isCustomer(role)) return '/';
  if (isSeller(role)) return '/seller';
  if (ROLE_GROUPS.CS_TEAM.includes(role)) return '/customer-service';
  if (ROLE_GROUPS.FINANCE_TEAM.includes(role)) return '/finance';
  if (ROLE_GROUPS.TRANSPORT_TEAM.includes(role)) return '/transport';
  if (isAnalyst(role)) return '/analyst';
  if (isAdmin(role)) return '/admin';
  return '/';
};
