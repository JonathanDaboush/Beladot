
/**
 * usePortalType
 *
 * Custom React hook to determine the portal type based on the current route.
 * Returns 'employee', 'seller', or 'user' depending on the pathname.
 *
 * Usage:
 *   const portalType = usePortalType();
 */
import { useAuth } from '../context/AuthContext';

export function usePortalType() {
  // Drive portal state from session permissions only
  const { activeRole } = useAuth();
  // Map roles to portal types; default to 'user' (Customer)
  if (activeRole === 'employee') return 'employee';
  if (activeRole === 'seller') return 'seller';
  if (activeRole === 'manager') return 'manager';
  return 'user';
}
