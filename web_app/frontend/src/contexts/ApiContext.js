import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const ApiContext = createContext();

export function useApi() {
  return useContext(ApiContext);
}

export function ApiProvider({ children }) {
  const [platforms, setPlatforms] = useState([]);
  const [config, setConfig] = useState({});
  const [loading, setLoading] = useState(false);

  const loadPlatforms = async () => {
    try {
      setLoading(true);
      const response = await api.get('/platforms');
      setPlatforms(response.data);
    } catch (error) {
      console.error('Error loading platforms:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadConfig = async () => {
    try {
      const response = await api.get('/config');
      setConfig(response.data);
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const saveConfig = async (newConfig) => {
    try {
      await api.post('/config', newConfig);
      setConfig(newConfig);
    } catch (error) {
      console.error('Error saving config:', error);
      throw error;
    }
  };

  const togglePlatformAutoUpload = async (platformName) => {
    try {
      await api.post(`/platforms/${platformName}/toggle`);
      await loadPlatforms();
    } catch (error) {
      console.error('Error toggling platform:', error);
      throw error;
    }
  };

  const getAccounts = async (platformName) => {
    try {
      const response = await api.get(`/platforms/${platformName}/accounts`);
      return response.data;
    } catch (error) {
      console.error('Error loading accounts:', error);
      throw error;
    }
  };

  const createAccount = async (platformName, accountData) => {
    try {
      const response = await api.post(`/platforms/${platformName}/accounts`, accountData);
      return response.data;
    } catch (error) {
      console.error('Error creating account:', error);
      throw error;
    }
  };

  const updateAccount = async (platformName, accountName, accountData) => {
    try {
      const response = await api.put(`/platforms/${platformName}/accounts/${accountName}`, accountData);
      return response.data;
    } catch (error) {
      console.error('Error updating account:', error);
      throw error;
    }
  };

  const deleteAccount = async (platformName, accountName) => {
    try {
      const response = await api.delete(`/platforms/${platformName}/accounts/${accountName}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting account:', error);
      throw error;
    }
  };

  const reauthenticateAccount = async (platformName, accountName, authData) => {
    try {
      const response = await api.post(`/platforms/${platformName}/accounts/${accountName}/reauth`, {
        name: accountName,
        ...authData
      });
      return response.data;
    } catch (error) {
      console.error('Error re-authenticating account:', error);
      throw error;
    }
  };

  const generateClipsFromUrl = async (platformName, accountName, url, mobileFormat = true) => {
    try {
      const response = await api.post(`/platforms/${platformName}/accounts/${accountName}/generate-from-url`, { 
        url,
        mobile_format: mobileFormat
      });
      return response.data;
    } catch (error) {
      console.error('Error generating clips from URL:', error);
      throw error;
    }
  };

  const generateClipsFromFile = async (platformName, accountName, file, mobileFormat = true) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('mobile_format', mobileFormat);
      const response = await api.post(`/platforms/${platformName}/accounts/${accountName}/generate-from-file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error generating clips from file:', error);
      throw error;
    }
  };

  const uploadContent = async (platformName, accountName) => {
    try {
      const response = await api.post(`/platforms/${platformName}/accounts/${accountName}/upload`);
      return response.data;
    } catch (error) {
      console.error('Error uploading content:', error);
      throw error;
    }
  };

  const getTaskStatus = async (taskId) => {
    try {
      const response = await api.get(`/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting task status:', error);
      throw error;
    }
  };

  const getDashboardStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      return response.data;
    } catch (error) {
      console.error('Error getting dashboard stats:', error);
      throw error;
    }
  };

  // Settings API functions
  const getSettings = async () => {
    try {
      const response = await api.get('/settings');
      return response.data;
    } catch (error) {
      console.error('Error getting settings:', error);
      throw error;
    }
  };

  const saveSettings = async (settings) => {
    try {
      const response = await api.post('/settings', settings);
      return response.data;
    } catch (error) {
      console.error('Error saving settings:', error);
      throw error;
    }
  };

  const updateSetting = async (section, key, value) => {
    try {
      const response = await api.put(`/settings/${section}/${key}`, { value });
      return response.data;
    } catch (error) {
      console.error('Error updating setting:', error);
      throw error;
    }
  };

  // Backup API functions
  const createBackup = async (includeVideos = false) => {
    try {
      const response = await api.post('/backup/create', null, {
        params: { include_videos: includeVideos }
      });
      return response.data;
    } catch (error) {
      console.error('Error creating backup:', error);
      throw error;
    }
  };

  const listBackups = async () => {
    try {
      const response = await api.get('/backup/list');
      return response.data;
    } catch (error) {
      console.error('Error listing backups:', error);
      throw error;
    }
  };

  const restoreBackup = async (filename) => {
    try {
      const response = await api.post(`/backup/restore/${filename}`);
      return response.data;
    } catch (error) {
      console.error('Error restoring backup:', error);
      throw error;
    }
  };

  const deleteBackup = async (filename) => {
    try {
      const response = await api.delete(`/backup/${filename}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting backup:', error);
      throw error;
    }
  };

  // Performance API functions
  const getPerformanceStats = async () => {
    try {
      const response = await api.get('/performance/stats');
      return response.data;
    } catch (error) {
      console.error('Error getting performance stats:', error);
      throw error;
    }
  };

  const getPerformanceWarnings = async () => {
    try {
      const response = await api.get('/performance/warnings');
      return response.data;
    } catch (error) {
      console.error('Error getting performance warnings:', error);
      throw error;
    }
  };

  // Security API functions
  const addIpToWhitelist = async (ipAddress) => {
    try {
      const response = await api.post('/security/whitelist', { ip_address: ipAddress });
      return response.data;
    } catch (error) {
      console.error('Error adding IP to whitelist:', error);
      throw error;
    }
  };

  const removeIpFromWhitelist = async (ipAddress) => {
    try {
      const response = await api.delete(`/security/whitelist/${ipAddress}`);
      return response.data;
    } catch (error) {
      console.error('Error removing IP from whitelist:', error);
      throw error;
    }
  };

  const checkPasswordStrength = async (password) => {
    try {
      const response = await api.post('/security/password/check', { password });
      return response.data;
    } catch (error) {
      console.error('Error checking password strength:', error);
      throw error;
    }
  };

  // Notification API functions
  const sendTestNotification = async (type) => {
    try {
      const response = await api.post('/notifications/test', { type });
      return response.data;
    } catch (error) {
      console.error('Error sending test notification:', error);
      throw error;
    }
  };

  const sendWeeklyReport = async () => {
    try {
      const response = await api.post('/notifications/weekly-report');
      return response.data;
    } catch (error) {
      console.error('Error sending weekly report:', error);
      throw error;
    }
  };

  // Import/Export settings
  const exportSettings = async () => {
    try {
      const response = await api.get('/settings/export');
      return response.data;
    } catch (error) {
      console.error('Error exporting settings:', error);
      throw error;
    }
  };

  const importSettings = async (settings) => {
    try {
      const response = await api.post('/settings/import', settings);
      return response.data;
    } catch (error) {
      console.error('Error importing settings:', error);
      throw error;
    }
  };

  const value = {
    platforms,
    config,
    loading,
    loadPlatforms,
    loadConfig,
    saveConfig,
    togglePlatformAutoUpload,
    getAccounts,
    createAccount,
    updateAccount,
    deleteAccount,
    reauthenticateAccount,
    generateClipsFromUrl,
    generateClipsFromFile,
    uploadContent,
    getTaskStatus,
    getDashboardStats,
    // Settings functions
    getSettings,
    saveSettings,
    updateSetting,
    // Backup functions
    createBackup,
    listBackups,
    restoreBackup,
    deleteBackup,
    // Performance functions
    getPerformanceStats,
    getPerformanceWarnings,
    // Security functions
    addIpToWhitelist,
    removeIpFromWhitelist,
    checkPasswordStrength,
    // Notification functions
    sendTestNotification,
    sendWeeklyReport,
    // Import/Export
    exportSettings,
    importSettings
  };

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  );
}