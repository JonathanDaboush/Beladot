import React, { useMemo } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ROLE_NAV = {
  user: [
    { to: '/catalog', label: 'Browse / Catalog' },
    { to: '/orders', label: 'Orders' },
    { to: '/wishlist', label: 'Wishlist' },
    { to: '/assistance', label: 'Assistance' },
  ],
  seller: [
    { to: '/catalog', label: 'Browse' },
    { to: '/seller/products', label: 'Products' },
    { to: '/seller/orders', label: 'Orders' },
    { to: '/seller/analytics', label: 'Analytics' },
    { to: '/seller/payouts', label: 'Payouts' },
    { to: '/seller/shipping', label: 'Shipping' },
  ],
  employee: [
    { to: '/employee/schedule', label: 'Schedule' },
    { to: '/employee/requests', label: 'Requests' },
    { to: '/employee/finance', label: 'Finance' },
    { to: '/employee/incidents', label: 'Incidents' },
    { to: '/employee/reimbursements', label: 'Reimbursements' },
  ],
  manager: [
    { to: '/employee/team', label: 'Team / Employees' },
    { to: '/employee/approvals', label: 'Approvals' },
    { to: '/employee/incidents', label: 'Incidents' },
    { to: '/employee/department', label: 'Department Overview' },
  ],
};

export default function NavBar() {
  const { activeRole } = useAuth();
  const items = useMemo(() => ROLE_NAV[activeRole] || ROLE_NAV.user, [activeRole]);
  return (
    <nav className="global-nav" aria-label="Primary">
      <ul>
        {items.map((item) => (
          <li key={item.to}>
            <NavLink to={item.to} className={({ isActive }) => isActive ? 'active' : ''} end>
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
