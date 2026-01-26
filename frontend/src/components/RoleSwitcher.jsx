import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ROLE_META } from './roles';
import Toast from './Toast';

export default function RoleSwitcher({ open, onClose }) {
  const { availableRoles, activeRole, setActiveRole } = useAuth();
  const navigate = useNavigate();
  const [switching, setSwitching] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMsg, setToastMsg] = useState('');

  const allowedRoles = useMemo(() => (availableRoles || []).filter((r) => Object.keys(ROLE_META).includes(r)), [availableRoles]);

  const handleSwitch = (role) => {
    if (!availableRoles.includes(role) || role === activeRole) return;
    setSwitching(true);
    setActiveRole(role);
    const home = ROLE_META[role]?.homePath || '/';
    // Visual confirmation could be a toast; keep simple inline for now
    setTimeout(() => {
      setSwitching(false);
      onClose?.();
      navigate(home);
      setToastMsg(`Switched to ${ROLE_META[role]?.name || role}`);
      setToastOpen(true);
    }, 150);
  };

  // Never render switcher unless user has more than one portal
  if (!open || !availableRoles || availableRoles.length <= 1) return null;
  return (
    <div className="role-switcher-panel" role="dialog" aria-label="Switch Role">
      <div className="role-switcher-header">
        <div className="title">Switch Role</div>
        <button className="close-btn" onClick={onClose} aria-label="Close">×</button>
      </div>
      <div className="role-switcher-content">
        <div className="current-role">
          <div className="label">Current Role</div>
          <div className="value">{ROLE_META[activeRole]?.name || activeRole}</div>
          <div className="desc">{ROLE_META[activeRole]?.description}</div>
        </div>
        <div className="available-roles">
          <div className="label">Available Roles</div>
          <ul>
            {allowedRoles.map((role) => {
              const isCurrent = role === activeRole;
              return (
                <li key={role} className={`role-option${isCurrent ? ' current' : ''}`}>
                  <button
                    className="role-btn"
                    disabled={switching || isCurrent}
                    onClick={() => handleSwitch(role)}
                  >
                    <div className="name">{ROLE_META[role]?.name || role}</div>
                    <div className="desc">{ROLE_META[role]?.description}</div>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
        {switching && <div className="inline-status">Switching roles…</div>}
      </div>
      <Toast open={toastOpen} message={toastMsg} onClose={() => setToastOpen(false)} />
    </div>
  );
}
