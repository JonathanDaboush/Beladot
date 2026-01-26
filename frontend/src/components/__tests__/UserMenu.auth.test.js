import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';

jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: { id: 1 }, isEmployee: false, isManager: false, isSeller: false }),
}));
// Also mock the path as imported by UserMenu (../context/AuthContext)

import UserMenu from '../UserMenu';

test('shows sign out when authenticated', () => {
  const onLogout = jest.fn();
  render(<UserMenu onLogout={onLogout} />);
  fireEvent.click(screen.getByRole('img', { name: /user/i }));
  const signOutItem = screen.getByText(/Sign out/i);
  expect(signOutItem).toBeInTheDocument();
  fireEvent.click(signOutItem);
  expect(onLogout).toHaveBeenCalled();
});
