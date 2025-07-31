import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar, 
  Users, 
  Video, 
  Clock,
  Target,
  Award,
  RefreshCw,
  Download,
  Filter,
  ChevronDown
} from 'lucide-react';

function Analytics() {
  const { getDashboardStats, platforms, loadPlatforms } = useApi();
  const [analytics, setAnalytics] = useState({
    overview: {
      totalUploads: 0,
      successRate: 0,
      totalAccounts: 0,
      activeAccounts: 0
    },
    platformStats: [],
    recentActivity: [],
    performance: {
      uploadsThisWeek: 0,
      uploadsThisMonth: 0,
      avgUploadTime: 0,
      errorRate: 5.2
    }
  });
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange, selectedPlatform]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      await loadPlatforms();
      
      // Simulate analytics data (in a real app, this would come from your backend)
      const mockAnalytics = {
        overview: {
          totalUploads: 1247,
          successRate: 94.8,
          totalAccounts: 12,
          activeAccounts: 8
        },
        platformStats: [
          {
            name: 'YouTube',
            icon: '🎥',
            uploads: 532,
            successRate: 96.2,
            avgViews: 15420,
            totalViews: 8203440,
            accounts: 4
          },
          {
            name: 'TikTok',
            icon: '🎵',
            uploads: 428,
            successRate: 93.1,
            avgViews: 8340,
            totalViews: 3569520,
            accounts: 3
          },
          {
            name: 'Instagram',
            icon: '📸',
            uploads: 187,
            successRate: 95.7,
            avgViews: 2140,
            totalViews: 400180,
            accounts: 3
          },
          {
            name: 'Twitter',
            icon: '🐦',
            uploads: 100,
            successRate: 92.0,
            avgViews: 1200,
            totalViews: 120000,
            accounts: 2
          }
        ],
        recentActivity: [
          { time: '2 hours ago', action: 'Video uploaded successfully', platform: 'YouTube', account: 'Gaming Channel', status: 'success' },
          { time: '4 hours ago', action: 'Content generation completed', platform: 'TikTok', account: 'Dance Account', status: 'success' },
          { time: '6 hours ago', action: 'Upload failed - authentication error', platform: 'Instagram', account: 'Photo Account', status: 'error' },
          { time: '1 day ago', action: 'Clips generated from URL', platform: 'YouTube', account: 'Tech Reviews', status: 'success' },
          { time: '1 day ago', action: 'Scheduled upload completed', platform: 'TikTok', account: 'Entertainment', status: 'success' }
        ],
        performance: {
          uploadsThisWeek: 47,
          uploadsThisMonth: 203,
          avgUploadTime: 142,
          errorRate: 5.2
        }
      };
      
      setAnalytics(mockAnalytics);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, subtitle, color = 'blue', trend }) => (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className={`p-3 rounded-full bg-${color}-100`}>
            <Icon className={`h-6 w-6 text-${color}-600`} />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
          </div>
        </div>
        {trend && (
          <div className={`flex items-center ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            <TrendingUp className="h-4 w-4 mr-1" />
            <span className="text-sm font-medium">{trend > 0 ? '+' : ''}{trend}%</span>
          </div>
        )}
      </div>
    </div>
  );

  const PlatformCard = ({ platform }) => (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <span className="text-2xl mr-3">{platform.icon}</span>
          <h3 className="font-semibold text-gray-900">{platform.name}</h3>
        </div>
        <span className="text-sm text-gray-500">{platform.accounts} accounts</span>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-sm text-gray-600">Total Uploads</p>
          <p className="text-xl font-bold text-gray-900">{platform.uploads.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Success Rate</p>
          <p className="text-xl font-bold text-green-600">{platform.successRate}%</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Avg. Views</p>
          <p className="text-xl font-bold text-blue-600">{platform.avgViews.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Total Views</p>
          <p className="text-xl font-bold text-purple-600">{(platform.totalViews / 1000000).toFixed(1)}M</p>
        </div>
      </div>
      
      <div className="mt-4">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full" 
            style={{ width: `${platform.successRate}%` }}
          ></div>
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
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
            <p className="text-gray-600">Comprehensive insights into your social media automation performance</p>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Time Range Filter */}
            <div className="relative">
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="1d">Last 24 hours</option>
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
              </select>
              <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
            
            {/* Platform Filter */}
            <div className="relative">
              <select
                value={selectedPlatform}
                onChange={(e) => setSelectedPlatform(e.target.value)}
                className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Platforms</option>
                <option value="YouTube">YouTube</option>
                <option value="TikTok">TikTok</option>
                <option value="Instagram">Instagram</option>
                <option value="Twitter">Twitter</option>
              </select>
              <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
            
            {/* Refresh Button */}
            <button
              onClick={loadAnalyticsData}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Video}
          title="Total Uploads"
          value={analytics.overview.totalUploads.toLocaleString()}
          subtitle="All time"
          color="blue"
          trend={12.5}
        />
        <StatCard
          icon={Target}
          title="Success Rate"
          value={`${analytics.overview.successRate}%`}
          subtitle="Upload success"
          color="green"
          trend={2.1}
        />
        <StatCard
          icon={Users}
          title="Active Accounts"
          value={`${analytics.overview.activeAccounts}/${analytics.overview.totalAccounts}`}
          subtitle="Accounts running"
          color="purple"
          trend={0}
        />
        <StatCard
          icon={Clock}
          title="Avg. Upload Time"
          value={`${analytics.performance.avgUploadTime}s`}
          subtitle="Processing time"
          color="orange"
          trend={-8.3}
        />
      </div>

      {/* Platform Performance */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Platform Performance</h2>
            <button className="flex items-center text-blue-600 hover:text-blue-700 text-sm font-medium">
              <Download className="h-4 w-4 mr-1" />
              Export Report
            </button>
          </div>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {analytics.platformStats.map((platform) => (
              <PlatformCard key={platform.name} platform={platform} />
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity & Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {analytics.recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.status === 'success' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{activity.action}</p>
                    <p className="text-xs text-gray-500">
                      {activity.platform} • {activity.account} • {activity.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Performance Metrics</h2>
          </div>
          <div className="p-6">
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Uploads This Week</span>
                  <span className="text-sm font-semibold">{analytics.performance.uploadsThisWeek}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Uploads This Month</span>
                  <span className="text-sm font-semibold">{analytics.performance.uploadsThisMonth}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '82%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Error Rate</span>
                  <span className="text-sm font-semibold text-red-600">{analytics.performance.errorRate}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-red-600 h-2 rounded-full" style={{ width: '5.2%' }}></div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Overall Health Score</span>
                  <div className="flex items-center">
                    <Award className="h-4 w-4 text-green-500 mr-1" />
                    <span className="text-sm font-semibold text-green-600">Excellent</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;