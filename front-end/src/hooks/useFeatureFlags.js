import { useState, useEffect } from 'react';

/**
 * Feature Flags Hook
 * Reads feature flags from environment and allows runtime toggling
 */
const useFeatureFlags = () => {
  const [flags, setFlags] = useState({
    analytics: process.env.REACT_APP_ENABLE_ANALYTICS === 'true',
    reviews: process.env.REACT_APP_ENABLE_REVIEWS === 'true',
    wishlists: process.env.REACT_APP_ENABLE_WISHLISTS === 'true',
    coupons: process.env.REACT_APP_ENABLE_COUPONS === 'true',
  });

  // Check if a feature is enabled
  const isEnabled = (featureName) => {
    return flags[featureName] === true;
  };

  // Toggle feature (for admin use)
  const toggleFeature = (featureName) => {
    setFlags((prev) => ({
      ...prev,
      [featureName]: !prev[featureName],
    }));
  };

  // Load feature flags from API (for admin control)
  const loadFeatureFlags = async () => {
    try {
      // This would call your admin API to get current feature flags
      // const response = await adminService.getFeatureFlags();
      // setFlags(response.data);
    } catch (error) {
      console.error('Failed to load feature flags:', error);
    }
  };

  useEffect(() => {
    // Optionally load flags from API on mount
    // loadFeatureFlags();
  }, []);

  return {
    flags,
    isEnabled,
    toggleFeature,
    loadFeatureFlags,
  };
};

export default useFeatureFlags;
