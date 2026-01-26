import React from 'react';
import { renderWithRouter } from '../../test-utils/renderWithRouter';
import { fireEvent, waitFor } from '@testing-library/react';
import ProfilePage from '../ProfilePage';

// Mock initial profile fetch
beforeEach(() => {
  jest.spyOn(global, 'fetch').mockImplementation((url, options) => {
    if (url === '/api/profile' && !options) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ user: { full_name: 'Jane Doe', shipping: '123 Street', payment: 'Visa **** 1111' } })
      });
    }
    if (url && url.startsWith('/api/profile/user')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
});

afterEach(() => {
  if (global.fetch.mockRestore) global.fetch.mockRestore();
});

describe('ProfilePage', () => {
  it('shows Not signed in when unauthorized', async () => {
    global.fetch.mockRestore && global.fetch.mockRestore();
    jest.spyOn(global, 'fetch').mockImplementation((url, options) => {
      if (url === '/api/profile' && !options) {
        return Promise.resolve({ ok: false, status: 401 });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    const { findByText } = renderWithRouter(<ProfilePage />);
    expect(await findByText('Not signed in')).toBeInTheDocument();
  });
  it('shows success toast after saving user info', async () => {
    const { findByText, getAllByText, getByDisplayValue, getByText } = renderWithRouter(<ProfilePage />);

    // Wait for initial load
    expect(await findByText('Profile')).toBeInTheDocument();
    expect(getByText('User Information')).toBeInTheDocument();

    // Enter edit mode
    fireEvent.click(getAllByText('Edit')[0]);

    // Change name
    const input = getByDisplayValue('Jane Doe');
    fireEvent.change(input, { target: { value: 'Jane A. Doe' } });

    // Save changes
    fireEvent.click(getByText('Save changes'));

    // Expect success toast
    expect(await findByText('Profile updated')).toBeInTheDocument();
  });

  it('shows error toast if save fails', async () => {
    const { findByText, getAllByText, getByDisplayValue, getByText } = renderWithRouter(<ProfilePage />);

    expect(await findByText('Profile')).toBeInTheDocument();

    fireEvent.click(getAllByText('Edit')[0]);
    const input = getByDisplayValue('Jane Doe');
    fireEvent.change(input, { target: { value: 'Jane B. Doe' } });
    // Override fetch to fail the save call
    global.fetch.mockImplementation((url, options) => {
      if (url && url.startsWith('/api/profile/user')) {
        return Promise.resolve({ ok: false });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    fireEvent.click(getByText('Save changes'));

    expect(await findByText('Could not save changes')).toBeInTheDocument();
  });
});
