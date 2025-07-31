import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { Users, Activity, CheckCircle, AlertCircle } from 'lucide-react';

function Dashboard() {
  const [stats, setStats] = useState({
    total_accounts: 0,
    active_accounts: 0,
    platforms_active: 0,
    total_platforms: 4
  });
  const [loading, setLoading] = useState(true);
  const { getDashboardStats, platforms, loadPlatforms } = useApi();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData] = await Promise.all([
        getDashboardStats(),
        loadPlatforms()
      ]);
      setStats(statsData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, color, description }) => (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
      <div className="flex items-center">
        <div className={`p-3 rounded-full ${color} bg-opacity-10`}>
          <Icon className={`h-6 w-6 ${color.replace('bg-', 'text-')}`} />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
        </div>
      </div>
    </div>
  );

  const PlatformCard = ({ platform }) => (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <span className="text-2xl mr-3">{platform.icon}</span>
          <div>
            <h3 className="font-semibold text-gray-900">{platform.name}</h3>
            <p className="text-sm text-gray-600">{platform.account_count} accounts</p>
          </div>
        </div>
        <div className="flex items-center">
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
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Monitor your social media automation status</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Users}
          title="Total Accounts"
          value={stats.total_accounts}
          color="bg-blue-500"
          description="Across all platforms"
        />
        <StatCard
          icon={Activity}
          title="Active Accounts"
          value={stats.active_accounts}
          color="bg-green-500"
          description="Currently running"
        />
        <StatCard
          icon={CheckCircle}
          title="Active Platforms"
          value={`${stats.platforms_active}/${stats.total_platforms}`}
          color="bg-purple-500"
          description="Auto-upload enabled"
        />
        <StatCard
          icon={AlertCircle}
          title="Status"
          value={stats.platforms_active > 0 ? "Running" : "Stopped"}
          color={stats.platforms_active > 0 ? "bg-green-500" : "bg-red-500"}
          description="System status"
        />
      </div>

      {/* Platforms Overview */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Platform Overview</h2>
          <button
            onClick={loadDashboardData}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            Refresh
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {platforms.map((platform) => (
            <PlatformCard key={platform.name} platform={platform} />
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-3">
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
            <div className="flex-1">
              <p className="text-sm text-gray-900">System initialized successfully</p>
              <p className="text-xs text-gray-500">Just now</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
            <div className="flex-1">
              <p className="text-sm text-gray-900">Dashboard loaded</p>
              <p className="text-xs text-gray-500">1 minute ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;