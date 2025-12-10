import React, { useState } from 'react';
import { Dropdown, Badge } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import './RoleSwitcher.css';

/**
 * Admin Role Switcher Component
 * Allows admins to view the app as different roles for testing/debugging
 */
const RoleSwitcher = () => {
  const { user, viewMode, switchViewMode, effectiveRole } = useAuth();
  const [show, setShow] = useState(false);

  // Only show for admin users
  if (!user || user.role !== 'admin') {
    return null;
  }

  const roles = [
    { value: 'admin', label: 'Admin (Full Access)', icon: '⚙️' },
    { value: 'divider', label: '--- View As ---', disabled: true },
    { value: 'customer', label: 'Customer', icon: '🛍️' },
    { value: 'seller', label: 'Seller', icon: '🏪' },
    { value: 'customer_service', label: 'Customer Service', icon: '🎧' },
    { value: 'finance', label: 'Finance', icon: '💰' },
    { value: 'transport', label: 'Transport', icon: '🚚' },
    { value: 'manager', label: 'Manager', icon: '👔' },
    { value: 'analyst', label: 'Analyst', icon: '📊' },
  ];

  const currentRoleLabel = roles.find((r) => r.value === effectiveRole)?.label || 'Unknown';
  const currentRoleIcon = roles.find((r) => r.value === effectiveRole)?.icon || '👤';

  return (
    <div className="role-switcher-container">
      <Dropdown show={show} onToggle={setShow} align="end">
        <Dropdown.Toggle variant="outline-primary" size="sm" className="role-switcher-toggle">
          <span className="role-icon">{currentRoleIcon}</span>
          <span className="role-label">
            View as: <strong>{currentRoleLabel}</strong>
          </span>
          {viewMode && (
            <Badge bg="warning" text="dark" className="ms-2">
              Impersonating
            </Badge>
          )}
        </Dropdown.Toggle>

        <Dropdown.Menu className="role-switcher-menu">
          <Dropdown.Header>Switch Role View</Dropdown.Header>
          {roles.map((role) => {
            if (role.value === 'divider') {
              return <Dropdown.Divider key={role.value} />;
            }

            return (
              <Dropdown.Item
                key={role.value}
                active={effectiveRole === role.value}
                onClick={() => switchViewMode(role.value)}
                disabled={role.disabled}
              >
                <span className="role-icon">{role.icon}</span>
                <span className="role-label">{role.label}</span>
                {effectiveRole === role.value && (
                  <span className="role-checkmark">✓</span>
                )}
              </Dropdown.Item>
            );
          })}
          
          <Dropdown.Divider />
          <Dropdown.Item className="text-muted" disabled>
            <small>
              💡 Role switching affects permissions and UI behavior
            </small>
          </Dropdown.Item>
        </Dropdown.Menu>
      </Dropdown>
    </div>
  );
};

export default RoleSwitcher;
