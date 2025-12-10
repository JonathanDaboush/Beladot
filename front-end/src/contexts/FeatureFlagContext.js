import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const FeatureFlagContext = createContext(null);

export const useFeatureFlags = () => {
  const context = useContext(FeatureFlagContext);
  if (!context) {
    throw new Error('useFeatureFlags must be used within FeatureFlagProvider');
  }
  return context;
};

export const FeatureFlagProvider = ({ children }) => {
  const { user } = useAuth();
  const [flags, setFlags] = useState({
    // Customer features
    newCheckoutFlow: false,
    enhancedSearch: true,
    productRecommendations: true,
    wishlistFeature: true,
    
    // Seller features
    bulkProductUpload: false,
    advancedAnalytics: true,
    autoInventoryAlerts: true,
    
    // Employee features
    advancedReporting: false,
    bulkApprovals: true,
    realTimeNotifications: true,
    
    // Admin features
    systemHealthMonitoring: true,
    auditLogViewer: true,
    featureFlagEditor: true,
  });

  // Load feature flags from localStorage or API
  useEffect(() => {
    const loadFlags = async () => {
      try {
        // Load from localStorage
        const savedFlags = localStorage.getItem('featureFlags');
        if (savedFlags) {
          setFlags((prev) => ({ ...prev, ...JSON.parse(savedFlags) }));
        }

        // Admin users can fetch from API
        if (user?.role === 'admin') {
          // TODO: Fetch from API endpoint
          // const response = await adminService.getFeatureFlags();
          // setFlags(response.data);
        }
      } catch (error) {
        console.error('Failed to load feature flags:', error);
      }
    };

    loadFlags();
  }, [user]);

  // Toggle a feature flag (admin only)
  const toggleFlag = (flagName) => {
    if (user?.role !== 'admin') {
      console.warn('Only admins can toggle feature flags');
      return;
    }

    setFlags((prev) => {
      const newFlags = { ...prev, [flagName]: !prev[flagName] };
      
      // Save to localStorage
      localStorage.setItem('featureFlags', JSON.stringify(newFlags));
      
      // TODO: Persist to API
      // adminService.updateFeatureFlag(flagName, newFlags[flagName]);
      
      return newFlags;
    });
  };

  // Check if a feature is enabled
  const isEnabled = (flagName) => {
    return flags[flagName] === true;
  };

  const value = {
    flags,
    toggleFlag,
    isEnabled,
  };

  return (
    <FeatureFlagContext.Provider value={value}>
      {children}
    </FeatureFlagContext.Provider>
  );
};
