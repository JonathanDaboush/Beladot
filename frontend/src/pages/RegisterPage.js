import React, { useState } from 'react';
import Button from '../components/Button';
import PageHeader from '../components/PageHeader';
// ...existing code...

const RegisterPage = () => {
  const [form, setForm] = useState({ full_name: '', email: '', password: '' });
  const [message, setMessage] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });
    if (res.ok) {
      window.location.href = '/login';
    } else {
      setMessage('Registration failed.');
    }
  };

  return (
    <div className="container py-4 d-flex justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
      <div className="w-100" style={{ maxWidth: '400px' }}>
        <PageHeader title="Create Account" subtitle="Register to manage orders and profile" />
        <form onSubmit={handleRegister} className="card p-4 shadow-sm">
          <div className="mb-3">
            <input
              type="text"
              className="form-control"
              placeholder="Full Name"
              value={form.full_name}
              onChange={e => setForm({ ...form, full_name: e.target.value })}
              required
            />
          </div>
          <div className="mb-3">
            <input
              type="email"
              className="form-control"
              placeholder="Email"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>
          <div className="mb-3">
            <input
              type="password"
              className="form-control"
              placeholder="Password"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>
          <Button type="submit" kind="primary">Create Account</Button>
        </form>
        {message && <div className="alert alert-danger mt-3 text-center">{message}</div>}
      </div>
    </div>
  );
};

export default RegisterPage;
