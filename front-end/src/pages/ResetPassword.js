import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { useNavigate, useSearchParams } from 'react-router-dom';
import authService from '../services/authService';

/**
 * Reset Password Page
 * User sets new password using token from email link
 */
const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [tokenValid, setTokenValid] = useState(true);
  const navigate = useNavigate();

  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      setTokenValid(false);
      setError('Invalid or missing reset token');
    }
  }, [token]);

  const validatePassword = () => {
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return false;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!validatePassword()) return;

    setLoading(true);

    try {
      await authService.resetPassword(token, password);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  if (!tokenValid) {
    return (
      <Container className="py-5">
        <Row className="justify-content-center">
          <Col md={6}>
            <Card>
              <Card.Body className="text-center p-5">
                <div style={{ fontSize: '64px', marginBottom: '20px' }}>❌</div>
                <h3>Invalid Reset Link</h3>
                <p className="text-muted">
                  This password reset link is invalid or has expired.
                </p>
                <Button variant="primary" onClick={() => navigate('/forgot-password')}>
                  Request New Link
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  if (success) {
    return (
      <Container className="py-5">
        <Row className="justify-content-center">
          <Col md={6}>
            <Card>
              <Card.Body className="text-center p-5">
                <div style={{ fontSize: '64px', marginBottom: '20px' }}>✅</div>
                <h3>Password Reset Successful</h3>
                <p className="text-muted">
                  Your password has been reset successfully. You can now log in with your new password.
                </p>
                <Button variant="primary" onClick={() => navigate('/login')}>
                  Go to Login
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  return (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col md={6}>
          <Card>
            <Card.Body className="p-4">
              <div className="text-center mb-4">
                <h2>Reset Your Password</h2>
                <p className="text-muted">
                  Enter your new password below.
                </p>
              </div>

              {error && (
                <Alert variant="danger" dismissible onClose={() => setError(null)}>
                  {error}
                </Alert>
              )}

              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>New Password</Form.Label>
                  <Form.Control
                    type="password"
                    placeholder="Enter new password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoFocus
                  />
                  <Form.Text className="text-muted">
                    Must be at least 8 characters
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Confirm Password</Form.Label>
                  <Form.Control
                    type="password"
                    placeholder="Confirm new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
                </Form.Group>

                {/* Password Strength Indicator */}
                {password && (
                  <div className="mb-3">
                    <small className="text-muted">Password strength:</small>
                    <div className="d-flex gap-1 mt-1">
                      <div className={`flex-fill bg-${password.length >= 8 ? 'success' : 'secondary'}`} style={{ height: '4px', borderRadius: '2px' }} />
                      <div className={`flex-fill bg-${password.length >= 12 && /[A-Z]/.test(password) ? 'success' : 'secondary'}`} style={{ height: '4px', borderRadius: '2px' }} />
                      <div className={`flex-fill bg-${password.length >= 12 && /[A-Z]/.test(password) && /[0-9]/.test(password) ? 'success' : 'secondary'}`} style={{ height: '4px', borderRadius: '2px' }} />
                    </div>
                  </div>
                )}

                <div className="d-grid">
                  <Button
                    variant="primary"
                    type="submit"
                    disabled={loading || !password || !confirmPassword}
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Resetting...
                      </>
                    ) : (
                      'Reset Password'
                    )}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ResetPassword;
