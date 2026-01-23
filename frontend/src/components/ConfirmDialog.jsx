import React from 'react';
import Button from './Button';

export default function ConfirmDialog({ open, title = 'Confirm', message, confirmLabel = 'Confirm', cancelLabel = 'Cancel', onConfirm, onCancel }) {
  if (!open) return null;
  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label={title}>
      <div className="modal-card">
        <div className="modal-header">
          <div className="modal-title h5">{title}</div>
          <button className="close-btn" aria-label="Close" onClick={onCancel}>×</button>
        </div>
        <div className="modal-body">
          <div className="muted" style={{ marginBottom: '0.75rem' }}>{message}</div>
        </div>
        <div className="modal-footer">
          <Button kind="destructive" onClick={onConfirm}>{confirmLabel}</Button>
          <Button kind="secondary" onClick={onCancel}>{cancelLabel}</Button>
        </div>
      </div>
    </div>
  );
}
