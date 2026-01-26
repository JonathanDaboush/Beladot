import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import Header from '../Header';
import InfoBox from '../InfoBox';
import { ErrorBoundary } from '../ErrorBoundary.jsx';
import { renderWithRouter } from '../../test-utils/renderWithRouter';

jest.mock('../../context/AuthContext', () => ({
  // Provide multiple roles so the role indicator & switcher are visible
  useAuth: () => ({ activeRole: 'user', availableRoles: ['user', 'seller'] }),
}));

jest.mock('../../hooks/usePortalType', () => ({
  usePortalType: () => 'user',
}));

beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve({ categories: [] }),
    })
  );
});

describe('Header', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });

  it('renders logo and role-scoped navigation', async () => {
    renderWithRouter(<Header />);
    await waitFor(() => expect(screen.getByText(/Bela/i)).toBeInTheDocument());
    // Nav includes user role item
    await waitFor(() => expect(screen.getByText('Browse / Catalog')).toBeInTheDocument());
  });

  it('shows role indicator pill and opens role switcher', async () => {
    renderWithRouter(<Header />);
    const indicator = await screen.findByRole('button', { name: /Current role/i });
    fireEvent.click(indicator);
    expect(await screen.findByRole('dialog', { name: /Switch Role/i })).toBeInTheDocument();
  });

  it('renders InfoBox with title and text', async () => {
    renderWithRouter(<InfoBox title="Tips" text="Always check variants" />);
    await waitFor(() => expect(screen.getByText('Tips')).toBeInTheDocument());
    await waitFor(() => expect(screen.getByText('Always check variants')).toBeInTheDocument());
  });

  it('ErrorBoundary renders fallback on error', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const ProblemChild = () => { throw new Error('Boom'); };
    renderWithRouter(
      <ErrorBoundary>
        <ProblemChild />
      </ErrorBoundary>
    );
    await waitFor(() => expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument());
    await waitFor(() => expect(screen.getByText(/Boom/i)).toBeInTheDocument());
    consoleSpy.mockRestore();
  });
});
