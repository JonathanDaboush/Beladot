import React from 'react';
import { useAuth } from '../context/AuthContext';
import { ROLE_META } from './roles';

export default function RoleIndicator({ onClick }) {
  const { activeRole, availableRoles } = useAuth();
  // Hide indicator entirely unless more than one portal is available
  if (!availableRoles || availableRoles.length <= 1) return null;
  const meta = ROLE_META[activeRole] || ROLE_META.user;
  return (
    <div
      className="role-indicator"
      style={{ backgroundColor: meta.pillColor }}
      onClick={onClick}
      role="button"
      aria-label={`Current role: ${meta.name}. Click to switch role.`}
    >
      {meta.name}
    </div>
  );
}
