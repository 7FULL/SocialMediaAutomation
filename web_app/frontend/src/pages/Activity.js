import React, { useState, useEffect } from 'react';
import { useApi } from '../contexts/ApiContext';
import { 
  Activity as ActivityIcon, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  XCircle,
  Search,
  Filter,
  Calendar,
  Download,
  RefreshCw,
  Play,
  Pause,
  Upload,
  Video,
  Settings,
  User,
  ChevronDown
} from 'lucide-react';

function Activity() {
  const [activities, setActivities] = useState([]);
  const [filteredActivities, setFilteredActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadActivities();
    
    // Auto-refresh every 10 seconds if enabled
    let interval;
    if (autoRefresh) {
      interval = setInterval(loadActivities, 10000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  useEffect(() => {
    filterActivities();
  }, [activities, searchTerm, statusFilter, platformFilter, typeFilter]);

  const loadActivities = async () => {
    try {
      setLoading(true);
      
      // Simulate activity data (in a real app, this would come from your backend)
      const mockActivities = [
        {
          id: 1,
          timestamp: new Date().toISOString(),
          type: 'upload',
          action: 'Video uploaded successfully',
          description: 'Gaming highlights clip uploaded to YouTube',
          platform: 'YouTube',
          account: 'Gaming Channel',
          status: 'success',
          duration: 45,
          details: { videoId: 'abc123', views: 0, size: '25MB' }
        },
        {
          id: 2,
          timestamp: new Date(Date.now() - 300000).toISOString(),
          type: 'generation',
          action: 'Content generation completed',
          description: 'Generated 5 clips from URL',
          platform: 'TikTok',
          account: 'Dance Account',
          status: 'success',
          duration: 180,
          details: { clipsGenerated: 5, sourceUrl: 'youtube.com/watch?v=example' }
        },
        {
          id: 3,
          timestamp: new Date(Date.now() - 600000).toISOString(),
          type: 'upload',
          action: 'Upload failed - authentication error',
          description: 'Failed to authenticate with Instagram API',
          platform: 'Instagram',
          account: 'Photo Account',
          status: 'error',
          duration: 12,
          details: { error: 'Token expired', errorCode: 401 }
        },
        {
          id: 4,
          timestamp: new Date(Date.now() - 900000).toISOString(),
          type: 'schedule',
          action: 'Scheduled upload triggered',
          description: 'Automatic upload started per schedule',
          platform: 'TikTok',
          account: 'Entertainment',
          status: 'processing',
          duration: null,
          details: { scheduledTime: '14:00', nextUpload: '16:00' }
        },
        {
          id: 5,
          timestamp: new Date(Date.now() - 1200000).toISOString(),
          type: 'account',
          action: 'Account authenticated',
          description: 'Successfully authenticated YouTube account',
          platform: 'YouTube',
          account: 'Tech Reviews',
          status: 'success',
          duration: 8,
          details: { method: 'OAuth2', scopes: ['youtube.upload'] }
        },
        {
          id: 6,
          timestamp: new Date(Date.now() - 1800000).toISOString(),
          type: 'generation',
          action: 'File processing started',
          description: 'Processing uploaded video file for clip generation',
          platform: 'YouTube',
          account: 'Music Channel',
          status: 'processing',
          duration: null,
          details: { fileName: 'concert_recording.mp4', fileSize: '1.2GB' }
        },
        {
          id: 7,
          timestamp: new Date(Date.now() - 2400000).toISOString(),
          type: 'system',
          action: 'Platform scheduler started',
          description: 'Auto-upload scheduler enabled for YouTube',
          platform: 'YouTube',
          account: 'System',
          status: 'success',
          duration: 2,
          details: { activeAccounts: 4, nextCheck: '15 minutes' }
        },
        {
          id: 8,
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          type: 'upload',
          action: 'Batch upload completed',
          description: 'Successfully uploaded 3 videos across platforms',
          platform: 'Multiple',
          account: 'Batch Job',
          status: 'success',
          duration: 320,
          details: { platforms: ['YouTube', 'TikTok', 'Twitter'], totalUploads: 3 }
        }
      ];
      
      setActivities(mockActivities);
    } catch (error) {
      console.error('Error loading activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterActivities = () => {
    let filtered = activities;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(activity =>
        activity.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
        activity.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        activity.account.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(activity => activity.status === statusFilter);
    }

    // Platform filter
    if (platformFilter !== 'all') {
      filtered = filtered.filter(activity => activity.platform === platformFilter);
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(activity => activity.type === typeFilter);
    }

    setFilteredActivities(filtered);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'processing':
        return <div className="h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'upload':
        return <Upload className="h-4 w-4 text-blue-500" />;
      case 'generation':
        return <Video className="h-4 w-4 text-purple-500" />;
      case 'schedule':
        return <Clock className="h-4 w-4 text-orange-500" />;
      case 'account':
        return <User className="h-4 w-4 text-green-500" />;
      case 'system':
        return <Settings className="h-4 w-4 text-gray-500" />;
      default:
        return <ActivityIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const ActivityItem = ({ activity }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          {getStatusIcon(activity.status)}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getTypeIcon(activity.type)}
              <h3 className="text-sm font-medium text-gray-900">{activity.action}</h3>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                {activity.status}
              </span>
              <span className="text-xs text-gray-500">{formatTimestamp(activity.timestamp)}</span>
            </div>
          </div>
          
          <p className="text-sm text-gray-600 mt-1">{activity.description}</p>
          
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span>{activity.platform}</span>
              <span>•</span>
              <span>{activity.account}</span>
              {activity.duration && (
                <>
                  <span>•</span>
                  <span>{activity.duration}s</span>
                </>
              )}
            </div>
          </div>
          
          {activity.details && (
            <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600">
              {Object.entries(activity.details).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="font-medium">{key}:</span>
                  <span>{typeof value === 'object' ? JSON.stringify(value) : value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Activity Monitor</h1>
            <p className="text-gray-600">Real-time log of all system activities and operations</p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                autoRefresh 
                  ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {autoRefresh ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
              {autoRefresh ? 'Pause' : 'Resume'} Auto-refresh
            </button>
            
            <button
              onClick={loadActivities}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search activities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          {/* Status Filter */}
          <div className="relative">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="success">Success</option>
              <option value="error">Error</option>
              <option value="processing">Processing</option>
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          </div>
          
          {/* Platform Filter */}
          <div className="relative">
            <select
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
              className="w-full appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Platforms</option>
              <option value="YouTube">YouTube</option>
              <option value="TikTok">TikTok</option>
              <option value="Instagram">Instagram</option>
              <option value="Twitter">Twitter</option>
              <option value="Multiple">Multiple</option>
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          </div>
          
          {/* Type Filter */}
          <div className="relative">
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              <option value="upload">Uploads</option>
              <option value="generation">Generation</option>
              <option value="schedule">Scheduled</option>
              <option value="account">Account</option>
              <option value="system">System</option>
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          </div>
          
          {/* Export Button */}
          <button className="flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
        
        <div className="mt-4 text-sm text-gray-600">
          Showing {filteredActivities.length} of {activities.length} activities
        </div>
      </div>

      {/* Activity Feed */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredActivities.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 border border-gray-200 text-center">
            <ActivityIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No activities found</h3>
            <p className="text-gray-600">
              {searchTerm || statusFilter !== 'all' || platformFilter !== 'all' || typeFilter !== 'all'
                ? 'Try adjusting your filters to see more activities.'
                : 'Activities will appear here as they happen.'}
            </p>
          </div>
        ) : (
          filteredActivities.map((activity) => (
            <ActivityItem key={activity.id} activity={activity} />
          ))
        )}
      </div>

      {/* Load More */}
      {filteredActivities.length > 0 && (
        <div className="text-center">
          <button className="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            Load More Activities
          </button>
        </div>
      )}
    </div>
  );
}

export default Activity;