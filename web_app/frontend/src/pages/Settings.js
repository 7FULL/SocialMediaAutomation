import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-hot-toast';
import { 
  Settings as SettingsIcon, 
  User, 
  Bell, 
  Shield, 
  Database,
  Download,
  Upload,
  RefreshCw,
  Save,
  Eye,
  EyeOff,
  Trash2,
  Plus,
  Edit,
  Check,
  X,
  AlertTriangle,
  Info,
  Key,
  Clock,
  Zap,
  Globe
} from 'lucide-react';

function Settings() {
  const { 
    getSettings, 
    saveSettings: saveSettingsApi, 
    createBackup, 
    listBackups, 
    restoreBackup, 
    deleteBackup,
    getPerformanceStats,
    addIpToWhitelist,
    removeIpFromWhitelist,
    sendTestNotification,
    exportSettings,
    importSettings
  } = useApi();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('general');
  const [loading, setLoading] = useState(false);
  const [showPasswords, setShowPasswords] = useState({});
  const [backups, setBackups] = useState([]);
  const [performanceStats, setPerformanceStats] = useState({});
  const [showBackupManager, setShowBackupManager] = useState(false);
  
  const [settings, setSettings] = useState({
    general: {
      appName: 'Social Media Automation Suite',
      timezone: 'UTC-5',
      language: 'en',
      theme: 'light',
      autoSave: true,
      maxConcurrentUploads: 3,
      defaultClipDuration: 57,
      retryAttempts: 3
    },
    notifications: {
      emailNotifications: true,
      uploadSuccess: true,
      uploadFailure: true,
      systemUpdates: false,
      maintenanceAlerts: true,
      weeklyReports: true,
      emailAddress: 'admin@example.com',
      mailjetApiKey: '',
      mailjetSecretKey: ''
    },
    security: {
      sessionTimeout: 30,
      requireStrongPasswords: true,
      twoFactorAuth: false,
      loginAttempts: 5,
      ipWhitelist: [],
      auditLogs: true,
      encryptionEnabled: true
    },
    performance: {
      uploadBandwidth: 10, // Mbps
      downloadBandwidth: 50, // Mbps
      maxFileSize: 1024, // MB
      compressionQuality: 85,
      parallelProcessing: true,
      cacheSize: 2048, // MB
      cleanupInterval: 24 // hours
    },
    backup: {
      autoBackup: true,
      backupInterval: 'daily',
      retentionDays: 30,
      includeVideos: false,
      backupLocation: '/backups',
      lastBackup: '2024-01-15T10:30:00Z'
    }
  });

  useEffect(() => {
    loadSettings();
    loadBackups();
    loadPerformanceStats();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const loadedSettings = await getSettings();
      setSettings(loadedSettings);
    } catch (error) {
      toast.error('Failed to load settings');
      console.error('Settings load error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadBackups = async () => {
    try {
      const backupList = await listBackups();
      setBackups(backupList);
    } catch (error) {
      console.error('Failed to load backups:', error);
    }
  };

  const loadPerformanceStats = async () => {
    try {
      const stats = await getPerformanceStats();
      setPerformanceStats(stats);
    } catch (error) {
      console.error('Failed to load performance stats:', error);
    }
  };

  const saveSettings = async () => {
    try {
      setLoading(true);
      await saveSettingsApi(settings);
      toast.success('Settings saved successfully!');
    } catch (error) {
      toast.error('Failed to save settings');
      console.error('Settings save error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (section, field, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const addToIpWhitelist = async () => {
    const ip = prompt('Enter IP address to whitelist:');
    if (ip && /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(ip)) {
      try {
        await addIpToWhitelist(ip);
        handleInputChange('security', 'ipWhitelist', [...settings.security.ipWhitelist, ip]);
        toast.success(`IP ${ip} added to whitelist`);
      } catch (error) {
        toast.error('Failed to add IP to whitelist');
      }
    } else if (ip) {
      toast.error('Please enter a valid IP address');
    }
  };

  const removeFromIpWhitelist = async (ip) => {
    try {
      await removeIpFromWhitelist(ip);
      handleInputChange('security', 'ipWhitelist', 
        settings.security.ipWhitelist.filter(item => item !== ip)
      );
      toast.success(`IP ${ip} removed from whitelist`);
    } catch (error) {
      toast.error('Failed to remove IP from whitelist');
    }
  };

  const handleExportSettings = async () => {
    try {
      const exportData = await exportSettings();
      const dataStr = JSON.stringify(exportData.data, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportData.filename);
      linkElement.click();
      
      toast.success('Settings exported successfully!');
    } catch (error) {
      toast.error('Failed to export settings');
    }
  };

  const handleImportSettings = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const importedSettings = JSON.parse(e.target.result);
          await importSettings(importedSettings);
          setSettings(importedSettings);
          toast.success('Settings imported successfully!');
        } catch (error) {
          toast.error('Invalid settings file or import failed');
        }
      };
      reader.readAsText(file);
    }
  };

  const handleCreateBackup = async () => {
    try {
      setLoading(true);
      const includeVideos = settings.backup.includeVideos;
      const result = await createBackup(includeVideos);
      
      if (result.success) {
        toast.success('Backup created successfully!');
        await loadBackups(); // Reload backup list
      } else {
        toast.error('Failed to create backup');
      }
    } catch (error) {
      toast.error('Failed to create backup');
      console.error('Backup creation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRestoreBackup = async (filename) => {
    if (window.confirm(`Are you sure you want to restore from backup "${filename}"? This will overwrite current settings.`)) {
      try {
        setLoading(true);
        const result = await restoreBackup(filename);
        
        if (result.success) {
          toast.success('Backup restored successfully! Page will reload.');
          setTimeout(() => window.location.reload(), 2000);
        } else {
          toast.error('Failed to restore backup');
        }
      } catch (error) {
        toast.error('Failed to restore backup');
        console.error('Backup restore error:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleDeleteBackup = async (filename) => {
    if (window.confirm(`Are you sure you want to delete backup "${filename}"?`)) {
      try {
        await deleteBackup(filename);
        toast.success('Backup deleted successfully!');
        await loadBackups(); // Reload backup list
      } catch (error) {
        toast.error('Failed to delete backup');
        console.error('Backup delete error:', error);
      }
    }
  };

  const handleTestNotification = async (type) => {
    try {
      const result = await sendTestNotification(type);
      toast.success('Test notification sent successfully!');
    } catch (error) {
      toast.error('Failed to send test notification');
      console.error('Test notification error:', error);
    }
  };

  const tabs = [
    { id: 'general', label: 'General', icon: SettingsIcon },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'performance', label: 'Performance', icon: Zap },
    { id: 'backup', label: 'Backup', icon: Database }
  ];

  const SettingSection = ({ title, description, children }) => (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {description && <p className="text-sm text-gray-600 mt-1">{description}</p>}
      </div>
      {children}
    </div>
  );

  const ToggleSwitch = ({ enabled, onChange, label, description }) => (
    <div className="flex items-center justify-between">
      <div>
        <label className="text-sm font-medium text-gray-900">{label}</label>
        {description && <p className="text-xs text-gray-500">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!enabled)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          enabled ? 'bg-blue-600' : 'bg-gray-200'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            enabled ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );

  const renderGeneralSettings = () => (
    <div>
      <SettingSection 
        title="Application Settings" 
        description="Basic configuration for the application"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Application Name</label>
            <input
              type="text"
              value={settings.general.appName}
              onChange={(e) => handleInputChange('general', 'appName', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Timezone</label>
            <select
              value={settings.general.timezone}
              onChange={(e) => handleInputChange('general', 'timezone', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="UTC-8">UTC-8 (Pacific)</option>
              <option value="UTC-5">UTC-5 (Eastern)</option>
              <option value="UTC+0">UTC+0 (GMT)</option>
              <option value="UTC+1">UTC+1 (CET)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
            <select
              value={settings.general.language}
              onChange={(e) => handleInputChange('general', 'language', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
            <select
              value={settings.general.theme}
              onChange={(e) => handleInputChange('general', 'theme', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto</option>
            </select>
          </div>
        </div>
      </SettingSection>

      <SettingSection 
        title="Upload Settings" 
        description="Configuration for content uploads and processing"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Max Concurrent Uploads</label>
            <input
              type="number"
              min="1"
              max="10"
              value={settings.general.maxConcurrentUploads}
              onChange={(e) => handleInputChange('general', 'maxConcurrentUploads', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Default Clip Duration (seconds)</label>
            <input
              type="number"
              min="10"
              max="300"
              value={settings.general.defaultClipDuration}
              onChange={(e) => handleInputChange('general', 'defaultClipDuration', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Retry Attempts</label>
            <input
              type="number"
              min="1"
              max="10"
              value={settings.general.retryAttempts}
              onChange={(e) => handleInputChange('general', 'retryAttempts', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div className="mt-4">
          <ToggleSwitch
            enabled={settings.general.autoSave}
            onChange={(value) => handleInputChange('general', 'autoSave', value)}
            label="Auto-save configuration"
            description="Automatically save changes as you make them"
          />
        </div>
      </SettingSection>
    </div>
  );

  const renderNotificationSettings = () => (
    <div>
      <SettingSection 
        title="Email Notifications" 
        description="Configure email notifications using Mailjet service"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
            <input
              type="email"
              value={settings.notifications.emailAddress}
              onChange={(e) => handleInputChange('notifications', 'emailAddress', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mailjet API Key</label>
              <div className="relative">
                <input
                  type={showPasswords.mailjetApiKey ? "text" : "password"}
                  value={settings.notifications.mailjetApiKey || ''}
                  onChange={(e) => handleInputChange('notifications', 'mailjetApiKey', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter Mailjet API Key"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(prev => ({ ...prev, mailjetApiKey: !prev.mailjetApiKey }))}
                  className="absolute right-2 top-2 text-gray-500 hover:text-gray-700"
                >
                  {showPasswords.mailjetApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mailjet Secret Key</label>
              <div className="relative">
                <input
                  type={showPasswords.mailjetSecretKey ? "text" : "password"}
                  value={settings.notifications.mailjetSecretKey || ''}
                  onChange={(e) => handleInputChange('notifications', 'mailjetSecretKey', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter Mailjet Secret Key"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(prev => ({ ...prev, mailjetSecretKey: !prev.mailjetSecretKey }))}
                  className="absolute right-2 top-2 text-gray-500 hover:text-gray-700"
                >
                  {showPasswords.mailjetSecretKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </div>
          
          <ToggleSwitch
            enabled={settings.notifications.emailNotifications}
            onChange={(value) => handleInputChange('notifications', 'emailNotifications', value)}
            label="Enable Email Notifications"
            description="Receive notifications via email using Mailjet"
          />
          
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-start">
              <Info className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-blue-900">Mailjet Setup Instructions</h4>
                <p className="text-sm text-blue-700 mt-1">
                  To use email notifications, you need to create a Mailjet account and get your API credentials:
                </p>
                <ol className="text-sm text-blue-700 mt-2 list-decimal list-inside space-y-1">
                  <li>Create a free account at <a href="https://www.mailjet.com" target="_blank" rel="noopener noreferrer" className="underline">mailjet.com</a></li>
                  <li>Go to Account Settings → API Keys</li>
                  <li>Copy your API Key and Secret Key</li>
                  <li>Paste them in the fields above</li>
                  <li>Save settings and test notifications</li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </SettingSection>

      <SettingSection 
        title="Notification Types" 
        description="Choose which events should trigger notifications"
      >
        <div className="space-y-4">
          <ToggleSwitch
            enabled={settings.notifications.uploadSuccess}
            onChange={(value) => handleInputChange('notifications', 'uploadSuccess', value)}
            label="Upload Success"
            description="Notify when uploads complete successfully"
          />
          
          <ToggleSwitch
            enabled={settings.notifications.uploadFailure}
            onChange={(value) => handleInputChange('notifications', 'uploadFailure', value)}
            label="Upload Failures"
            description="Notify when uploads fail"
          />
          
          <ToggleSwitch
            enabled={settings.notifications.systemUpdates}
            onChange={(value) => handleInputChange('notifications', 'systemUpdates', value)}
            label="System Updates"
            description="Notify about system updates and new features"
          />
          
          <ToggleSwitch
            enabled={settings.notifications.maintenanceAlerts}
            onChange={(value) => handleInputChange('notifications', 'maintenanceAlerts', value)}
            label="Maintenance Alerts"
            description="Notify about scheduled maintenance"
          />
          
          <ToggleSwitch
            enabled={settings.notifications.weeklyReports}
            onChange={(value) => handleInputChange('notifications', 'weeklyReports', value)}
            label="Weekly Reports"
            description="Receive weekly activity summaries"
          />
        </div>
      </SettingSection>

      <SettingSection 
        title="Test Notifications" 
        description="Send test notifications to verify your email configuration"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => handleTestNotification('uploadSuccess')}
            className="flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Check className="h-4 w-4 mr-2" />
            Test Upload Success
          </button>
          
          <button
            onClick={() => handleTestNotification('uploadFailure')}
            className="flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <X className="h-4 w-4 mr-2" />
            Test Upload Failure
          </button>
          
          <button
            onClick={() => handleTestNotification('weeklyReport')}
            className="flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Clock className="h-4 w-4 mr-2" />
            Test Weekly Report
          </button>
        </div>
      </SettingSection>
    </div>
  );

  const renderSecuritySettings = () => (
    <div>
      <SettingSection 
        title="Authentication" 
        description="Configure authentication and session settings"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Session Timeout (minutes)</label>
            <input
              type="number"
              min="5"
              max="480"
              value={settings.security.sessionTimeout}
              onChange={(e) => handleInputChange('security', 'sessionTimeout', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Max Login Attempts</label>
            <input
              type="number"
              min="3"
              max="10"
              value={settings.security.loginAttempts}
              onChange={(e) => handleInputChange('security', 'loginAttempts', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div className="mt-4 space-y-4">
          <ToggleSwitch
            enabled={settings.security.requireStrongPasswords}
            onChange={(value) => handleInputChange('security', 'requireStrongPasswords', value)}
            label="Require Strong Passwords"
            description="Enforce password complexity requirements"
          />
          
          <ToggleSwitch
            enabled={settings.security.twoFactorAuth}
            onChange={(value) => handleInputChange('security', 'twoFactorAuth', value)}
            label="Two-Factor Authentication"
            description="Require 2FA for enhanced security"
          />
          
          <ToggleSwitch
            enabled={settings.security.auditLogs}
            onChange={(value) => handleInputChange('security', 'auditLogs', value)}
            label="Audit Logging"
            description="Log all user actions for security auditing"
          />
          
          <ToggleSwitch
            enabled={settings.security.encryptionEnabled}
            onChange={(value) => handleInputChange('security', 'encryptionEnabled', value)}
            label="Data Encryption"
            description="Encrypt sensitive data at rest"
          />
        </div>
      </SettingSection>

      <SettingSection 
        title="IP Whitelist" 
        description="Restrict access to specific IP addresses"
      >
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Allowed IP Addresses</span>
            <button
              onClick={addToIpWhitelist}
              className="flex items-center px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              <Plus className="h-4 w-4 mr-1" />
              Add IP
            </button>
          </div>
          
          {settings.security.ipWhitelist.length === 0 ? (
            <p className="text-sm text-gray-500 italic">No IP restrictions configured</p>
          ) : (
            <div className="space-y-2">
              {settings.security.ipWhitelist.map((ip, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-lg">
                  <span className="text-sm font-mono">{ip}</span>
                  <button
                    onClick={() => removeFromIpWhitelist(ip)}
                    className="text-red-600 hover:text-red-700 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </SettingSection>
    </div>
  );

  const renderPerformanceSettings = () => (
    <div>
      <SettingSection 
        title="Bandwidth Limits" 
        description="Configure upload and download bandwidth limits"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Upload Bandwidth (Mbps)</label>
            <input
              type="number"
              min="1"
              max="1000"
              value={settings.performance.uploadBandwidth}
              onChange={(e) => handleInputChange('performance', 'uploadBandwidth', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Download Bandwidth (Mbps)</label>
            <input
              type="number"
              min="1"
              max="1000"
              value={settings.performance.downloadBandwidth}
              onChange={(e) => handleInputChange('performance', 'downloadBandwidth', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </SettingSection>

      <SettingSection 
        title="File Processing" 
        description="Configure file size limits and processing options"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Max File Size (MB)</label>
            <input
              type="number"
              min="100"
              max="10240"
              value={settings.performance.maxFileSize}
              onChange={(e) => handleInputChange('performance', 'maxFileSize', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Compression Quality (%)</label>
            <input
              type="number"
              min="10"
              max="100"
              value={settings.performance.compressionQuality}
              onChange={(e) => handleInputChange('performance', 'compressionQuality', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Cache Size (MB)</label>
            <input
              type="number"
              min="512"
              max="8192"
              value={settings.performance.cacheSize}
              onChange={(e) => handleInputChange('performance', 'cacheSize', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Cleanup Interval (hours)</label>
            <input
              type="number"
              min="1"
              max="168"
              value={settings.performance.cleanupInterval}
              onChange={(e) => handleInputChange('performance', 'cleanupInterval', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div className="mt-4">
          <ToggleSwitch
            enabled={settings.performance.parallelProcessing}
            onChange={(value) => handleInputChange('performance', 'parallelProcessing', value)}
            label="Enable Parallel Processing"
            description="Process multiple files simultaneously for better performance"
          />
        </div>
      </SettingSection>

      <SettingSection 
        title="System Performance" 
        description="Current system performance metrics"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">CPU Usage</div>
            <div className="text-2xl font-bold text-blue-600">
              {performanceStats.cpu_usage ? `${performanceStats.cpu_usage.toFixed(1)}%` : 'Loading...'}
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Memory Usage</div>
            <div className="text-2xl font-bold text-green-600">
              {performanceStats.memory_usage ? `${performanceStats.memory_usage.toFixed(1)}%` : 'Loading...'}
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Disk Usage</div>
            <div className="text-2xl font-bold text-yellow-600">
              {performanceStats.disk_usage ? `${performanceStats.disk_usage.toFixed(1)}%` : 'Loading...'}
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Active Processes</div>
            <div className="text-2xl font-bold text-purple-600">
              {performanceStats.active_processes || 'Loading...'}
            </div>
          </div>
        </div>
        
        <div className="mt-4">
          <button
            onClick={loadPerformanceStats}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Stats
          </button>
        </div>
      </SettingSection>
    </div>
  );

  const renderBackupSettings = () => (
    <div>
      <SettingSection 
        title="Backup Configuration" 
        description="Configure automatic backups and retention policies"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Backup Interval</label>
            <select
              value={settings.backup.backupInterval}
              onChange={(e) => handleInputChange('backup', 'backupInterval', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Retention Days</label>
            <input
              type="number"
              min="1"
              max="365"
              value={settings.backup.retentionDays}
              onChange={(e) => handleInputChange('backup', 'retentionDays', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Backup Location</label>
            <input
              type="text"
              value={settings.backup.backupLocation}
              onChange={(e) => handleInputChange('backup', 'backupLocation', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="/path/to/backup/directory"
            />
          </div>
        </div>
        
        <div className="mt-4 space-y-4">
          <ToggleSwitch
            enabled={settings.backup.autoBackup}
            onChange={(value) => handleInputChange('backup', 'autoBackup', value)}
            label="Enable Automatic Backups"
            description="Automatically backup configuration and data"
          />
          
          <ToggleSwitch
            enabled={settings.backup.includeVideos}
            onChange={(value) => handleInputChange('backup', 'includeVideos', value)}
            label="Include Video Files"
            description="Include video files in backups (significantly increases size)"
          />
        </div>
        
        {settings.backup.lastBackup && (
          <div className="mt-4 p-3 bg-green-50 rounded-lg">
            <div className="flex items-center">
              <Check className="h-5 w-5 text-green-500 mr-2" />
              <span className="text-sm text-green-700">
                Last backup: {new Date(settings.backup.lastBackup).toLocaleString()}
              </span>
            </div>
          </div>
        )}
        
        <div className="mt-4 space-y-4">
          <div className="flex space-x-3">
            <button 
              onClick={handleCreateBackup}
              disabled={loading}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <Download className="h-4 w-4 mr-2" />
              Create Backup Now
            </button>
            
            <button 
              onClick={() => setShowBackupManager(true)}
              className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <Upload className="h-4 w-4 mr-2" />
              Manage Backups
            </button>
          </div>

          {/* Backup List */}
          {backups.length > 0 && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Recent Backups</h4>
              <div className="space-y-2">
                {backups.slice(0, 3).map((backup, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">{backup.filename}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-500">{new Date(backup.created).toLocaleDateString()}</span>
                      <button
                        onClick={() => handleRestoreBackup(backup.filename)}
                        className="text-blue-600 hover:text-blue-700"
                      >
                        Restore
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </SettingSection>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Settings</h1>
            <p className="text-gray-600">Configure application settings and preferences</p>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="relative">
              <input
                type="file"
                accept=".json"
                onChange={handleImportSettings}
                className="hidden"
                id="import-settings"
              />
              <label
                htmlFor="import-settings"
                className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors cursor-pointer"
              >
                <Upload className="h-4 w-4 mr-2" />
                Import
              </label>
            </div>
            
            <button
              onClick={handleExportSettings}
              className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <Download className="h-4 w-4 mr-2" />
              Export
            </button>
            
            <button
              onClick={saveSettings}
              disabled={loading}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              Save Changes
            </button>
          </div>
        </div>
      </div>

      {/* Settings Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <nav className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-3 py-2 text-left rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="h-5 w-5 mr-3" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          {activeTab === 'general' && renderGeneralSettings()}
          {activeTab === 'notifications' && renderNotificationSettings()}
          {activeTab === 'security' && renderSecuritySettings()}
          {activeTab === 'performance' && renderPerformanceSettings()}
          {activeTab === 'backup' && renderBackupSettings()}
        </div>
      </div>
    </div>
  );
}

export default Settings;