import React from 'react';
import { render, screen } from '@testing-library/react';
import Header from '../Header';

jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ isEmployee: false, isSeller: false }),
}));

jest.mock('../../hooks/usePortalType', () => ({
  usePortalType: () => 'user',
}));

describe('Header (error path)', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders without categories when API returns empty payload', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({ json: () => Promise.resolve({}) })
    );
    render(<Header />);
    expect(await screen.findByPlaceholderText(/Search products/i)).toBeInTheDocument();
    // Ensure a known category label is not present since payload is empty
    expect(screen.queryByText('Food')).not.toBeInTheDocument();
  });
});
