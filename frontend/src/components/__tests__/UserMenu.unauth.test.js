import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';

jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: null, isEmployee: false, isManager: false, isSeller: false }),
}));

import UserMenu from '../UserMenu';

test('shows auth actions and profile message when not authenticated', () => {
  const onLogout = jest.fn();
  render(<UserMenu onLogout={onLogout} />);
  fireEvent.click(screen.getByRole('img', { name: /user/i }));
  expect(screen.getByText(/Sign in/i)).toBeInTheDocument();
  expect(screen.getByText(/Create Account/i)).toBeInTheDocument();
  expect(screen.getByText(/Forgot Password/i)).toBeInTheDocument();
  // Profile navigates to page; dropdown no longer shows inline message
});
