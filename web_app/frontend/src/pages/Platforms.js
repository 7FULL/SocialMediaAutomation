import React, { useEffect, useState } from 'react';
import { useApi } from '../contexts/ApiContext';
import { Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { 
  ToggleLeft,
  Users, 
  Settings, 
  ArrowRight, 
  CheckCircle, 
  AlertCircle,
  RefreshCw
} from 'lucide-react';

function Platforms() {
  const { platforms, loadPlatforms, togglePlatformAutoUpload } = useApi();
  const [loading, setLoading] = useState(true);
  const [toggleLoading, setToggleLoading] = useState({});

  useEffect(() => {
    loadPlatformsData();
  }, []);

  const loadPlatformsData = async () => {
    try {
      setLoading(true);
      await loadPlatforms();
    } catch (error) {
      toast.error('Failed to load platforms');
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePlatform = async (platformName) => {
    setToggleLoading({ ...toggleLoading, [platformName]: true });
    try {
      await togglePlatformAutoUpload(platformName);
      // Reload platforms data to update the UI state
      await loadPlatforms();
      toast.success(`${platformName} auto-upload toggled successfully`);
    } catch (error) {
      toast.error('Failed to toggle platform');
    } finally {
      setToggleLoading({ ...toggleLoading, [platformName]: false });
    }
  };

  const PlatformCard = ({ platform }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <span className="text-3xl mr-4">{platform.icon}</span>
            <div>
              <h3 className="text-xl font-semibold text-gray-900">{platform.name}</h3>
              <p className="text-sm text-gray-600">{platform.account_count} accounts configured</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {platform.active ? (
              <div className="flex items-center text-green-600">
                <CheckCircle className="h-5 w-5 mr-1" />
                <span className="text-sm font-medium">Active</span>
              </div>
            ) : (
              <div className="flex items-center text-gray-400">
                <AlertCircle className="h-5 w-5 mr-1" />
                <span className="text-sm font-medium">Inactive</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => handleTogglePlatform(platform.name)}
              disabled={toggleLoading[platform.name]}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                platform.active
                  ? 'bg-red-100 text-red-700 hover:bg-red-200'
                  : 'bg-green-100 text-green-700 hover:bg-green-200'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {toggleLoading[platform.name] ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <ToggleLeft className="h-4 w-4 mr-2" />
              )}
              {platform.active ? 'Disable' : 'Enable'} Auto-Upload
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <Link
              to={`/platforms/${platform.name}`}
              className="flex items-center px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm font-medium"
            >
              <Settings className="h-4 w-4 mr-2" />
              Manage
              <ArrowRight className="h-4 w-4 ml-2" />
            </Link>
          </div>
        </div>
      </div>

      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Accounts:</span>
          <span className="font-medium text-gray-900">{platform.account_count}</span>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Social Media Platforms</h1>
            <p className="text-gray-600">Manage your social media automation platforms</p>
          </div>
          <button
            onClick={loadPlatformsData}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Platforms Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {platforms.map((platform) => (
          <PlatformCard key={platform.name} platform={platform} />
        ))}
      </div>

      {/* Summary Stats */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Platform Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {platforms.filter(p => p.active).length}
            </div>
            <div className="text-sm text-gray-600">Active Platforms</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {platforms.reduce((sum, p) => sum + p.account_count, 0)}
            </div>
            <div className="text-sm text-gray-600">Total Accounts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {platforms.length}
            </div>
            <div className="text-sm text-gray-600">Available Platforms</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Platforms;