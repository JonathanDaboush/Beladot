import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import Button from '../components/Button';
import Toast from '../components/Toast';
import './ProfilePage.css';

const ProfilePage = () => {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState('loading'); // loading | ready | unauth
  const [editMode, setEditMode] = useState({ user: false, shipping: false, payment: false });
  const [form, setForm] = useState({});
  const [toast, setToast] = useState({ open: false, kind: 'success', message: '' });

  useEffect(() => {
    let mounted = true;
    fetch('/api/profile')
      .then(async res => {
        if (!mounted) return;
        if (res.status === 401 || res.status === 403) {
          setStatus('unauth');
          return null;
        }
        if (!res.ok) {
          setStatus('unauth');
          return null;
        }
        const data = await res.json();
        if (!data || !data.user) {
          setStatus('unauth');
          return null;
        }
        setUser(data.user);
        setForm(data.user);
        setStatus('ready');
      })
      .catch(() => {
        if (mounted) setStatus('unauth');
      });
    return () => { mounted = false; };
  }, []);

  const handleEdit = section => setEditMode({ ...editMode, [section]: true });
  const handleCancel = section => {
    setEditMode({ ...editMode, [section]: false });
    setForm(user);
  };
  const handleSave = section => {
    fetch(`/api/profile/${section}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    }).then(res => {
      if (!res.ok) throw new Error('Failed to save changes');
      setEditMode({ ...editMode, [section]: false });
      setUser(form);
      setToast({ open: true, kind: 'success', message: 'Profile updated' });
    }).catch(() => setToast({ open: true, kind: 'error', message: 'Could not save changes' }));
  };

  if (status === 'loading') return <div className="profile-loading">Loading...</div>;

  if (status === 'unauth') return (
    <div className="profile-page">
      <PageHeader title="Profile" subtitle="Manage your account and preferences" />
      <section className="profile-section">
        <h3>Not signed in</h3>
        <p>Please sign in to view your profile.</p>
      </section>
    </div>
  );

  return (
    <div className="profile-page">
      <PageHeader title="Profile" subtitle="Manage your account and preferences" />
      <section className="profile-section">
        <h3>User Information</h3>
        {editMode.user ? (
          <>
            <input value={form.full_name || ''} onChange={e => setForm({ ...form, full_name: e.target.value })} />
            <Button kind="primary" onClick={() => handleSave('user')}>Save changes</Button>
            <Button kind="secondary" onClick={() => handleCancel('user')}>Cancel</Button>
          </>
        ) : (
          <>
            <div>Name: {user.full_name}</div>
            <Button kind="secondary" onClick={() => handleEdit('user')}>Edit</Button>
          </>
        )}
      </section>
      <section className="profile-section">
        <h3>Shipping Information</h3>
        {user.shipping ? (
          editMode.shipping ? (
            <>
              <input value={form.shipping || ''} onChange={e => setForm({ ...form, shipping: e.target.value })} />
              <Button kind="primary" onClick={() => handleSave('shipping')}>Save changes</Button>
              <Button kind="secondary" onClick={() => handleCancel('shipping')}>Cancel</Button>
            </>
          ) : (
            <>
              <div>{user.shipping}</div>
              <Button kind="secondary" onClick={() => handleEdit('shipping')}>Edit</Button>
            </>
          )
        ) : (
          <Button kind="primary" onClick={() => handleEdit('shipping')}>Add shipping info</Button>
        )}
      </section>
      <section className="profile-section">
        <h3>Payment Information</h3>
        {user.payment ? (
          editMode.payment ? (
            <>
              <input value={form.payment || ''} onChange={e => setForm({ ...form, payment: e.target.value })} />
              <Button kind="primary" onClick={() => handleSave('payment')}>Save changes</Button>
              <Button kind="secondary" onClick={() => handleCancel('payment')}>Cancel</Button>
            </>
          ) : (
            <>
              <div>{user.payment}</div>
              <Button kind="secondary" onClick={() => handleEdit('payment')}>Edit</Button>
            </>
          )
        ) : (
          <Button kind="primary" onClick={() => handleEdit('payment')}>Add payment method</Button>
        )}
      </section>
      <Button kind="danger" className="delete-account-btn" onClick={async () => {
        const res = await fetch('/api/disable_user_account', { method: 'POST' });
        if (res.status === 401 || res.status === 403) {
          setToast({ open: true, kind: 'error', message: 'Unauthorized or forbidden' });
          return;
        }
        window.location.href = '/login';
      }}>Delete account</Button>
      <Toast open={toast.open} kind={toast.kind} message={toast.message} onClose={() => setToast({ ...toast, open: false })} />
    </div>
  );
};

export default ProfilePage;
