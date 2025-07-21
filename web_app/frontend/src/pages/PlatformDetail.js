import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApi } from '../contexts/ApiContext';
import { toast } from 'react-hot-toast';
import { useDropzone } from 'react-dropzone';
import PlatformAuthForm from '../components/PlatformAuthForm';
import { 
  ArrowLeft, 
  Plus, 
  Edit, 
  Trash2, 
  Upload, 
  Link as LinkIcon,
  FileVideo,
  Calendar,
  Settings,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Clock,
  Play,
  Pause,
  X
} from 'lucide-react';

function PlatformDetail() {
  const { platformName } = useParams();
  const navigate = useNavigate();
  const { 
    getAccounts, 
    createAccount, 
    updateAccount, 
    deleteAccount, 
    generateClipsFromUrl,
    generateClipsFromFile,
    uploadContent,
    getTaskStatus 
  } = useApi();

  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [showAccountEditor, setShowAccountEditor] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [showContentGenerator, setShowContentGenerator] = useState(false);
  const [activeTasks, setActiveTasks] = useState({});

  // Form states
  const [accountForm, setAccountForm] = useState({
    name: '',
    active: true,
    description: '',
    tags: '',
    title: '',
    category_id: '',
    clip_duration: 57
  });

  const [scheduleForm, setScheduleForm] = useState({
    Monday: [], Tuesday: [], Wednesday: [], Thursday: [],
    Friday: [], Saturday: [], Sunday: []
  });

  const [contentForm, setContentForm] = useState({
    url: '',
    file: null,
    type: 'url' // 'url' or 'file'
  });

  const [authData, setAuthData] = useState({});

  const platformIcons = {
    'YouTube': '🎥',
    'TikTok': '🎵',
    'Instagram': '📸',
    'Twitter': '🐦'
  };

  useEffect(() => {
    loadAccounts();
  }, [platformName]);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const data = await getAccounts(platformName);
      setAccounts(data);
    } catch (error) {
      toast.error('Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = async () => {
    try {
      const accountData = {
        ...accountForm,
        ...authData
      };
      
      const response = await createAccount(platformName, accountData);
      
      if (response.authenticated) {
        toast.success(`Account created successfully! ${response.auth_message}`);
      } else {
        toast.error(`Account created but authentication failed: ${response.auth_message}`);
      }
      
      setShowAddAccount(false);
      setAccountForm({
        name: '',
        active: true,
        description: '',
        tags: '',
        title: '',
        category_id: '',
        clip_duration: 57
      });
      setAuthData({});
      loadAccounts();
    } catch (error) {
      toast.error('Failed to create account');
    }
  };

  const handleUpdateAccount = async () => {
    try {
      await updateAccount(platformName, selectedAccount.name, {
        ...selectedAccount,
        schedule: scheduleForm
      });
      toast.success('Account updated successfully!');
      setShowAccountEditor(false);
      setSelectedAccount(null);
      loadAccounts();
    } catch (error) {
      toast.error('Failed to update account');
    }
  };

  const handleDeleteAccount = async (accountName) => {
    if (window.confirm(`Are you sure you want to delete account "${accountName}"?`)) {
      try {
        await deleteAccount(platformName, accountName);
        toast.success('Account deleted successfully!');
        loadAccounts();
      } catch (error) {
        toast.error('Failed to delete account');
      }
    }
  };

  const handleGenerateContent = async () => {
    try {
      let response;
      if (contentForm.type === 'url') {
        response = await generateClipsFromUrl(platformName, selectedAccount.name, contentForm.url);
      } else {
        response = await generateClipsFromFile(platformName, selectedAccount.name, contentForm.file);
      }
      
      const taskId = response.task_id;
      setActiveTasks(prev => ({ ...prev, [taskId]: { status: 'processing', progress: 0 } }));
      
      toast.success('Content generation started!');
      setShowContentGenerator(false);
      setContentForm({ url: '', file: null, type: 'url' });
      
      // Poll for task status
      pollTaskStatus(taskId);
    } catch (error) {
      toast.error('Failed to start content generation');
    }
  };

  const handleUploadContent = async (accountName) => {
    try {
      const response = await uploadContent(platformName, accountName);
      const taskId = response.task_id;
      setActiveTasks(prev => ({ ...prev, [taskId]: { status: 'processing', progress: 0 } }));
      
      toast.success('Content upload started!');
      
      // Poll for task status
      pollTaskStatus(taskId);
    } catch (error) {
      toast.error('Failed to start content upload');
    }
  };

  const pollTaskStatus = async (taskId) => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await getTaskStatus(taskId);
        setActiveTasks(prev => ({ ...prev, [taskId]: status }));
        
        if (status.status === 'completed') {
          toast.success(status.message);
          clearInterval(pollInterval);
        } else if (status.status === 'failed') {
          toast.error(status.message);
          clearInterval(pollInterval);
        }
      } catch (error) {
        clearInterval(pollInterval);
      }
    }, 2000);
  };

  const openAccountEditor = (account) => {
    setSelectedAccount(account);
    setScheduleForm(account.schedule || {
      Monday: [], Tuesday: [], Wednesday: [], Thursday: [],
      Friday: [], Saturday: [], Sunday: []
    });
    setShowAccountEditor(true);
  };

  const addScheduleTime = (day, time) => {
    if (time && !scheduleForm[day].includes(time)) {
      setScheduleForm(prev => ({
        ...prev,
        [day]: [...prev[day], time].sort()
      }));
    }
  };

  const removeScheduleTime = (day, time) => {
    setScheduleForm(prev => ({
      ...prev,
      [day]: prev[day].filter(t => t !== time)
    }));
  };

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setContentForm(prev => ({ ...prev, file, type: 'file' }));
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv']
    },
    maxFiles: 1
  });

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
          <div className="flex items-center">
            <button
              onClick={() => navigate('/platforms')}
              className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div className="flex items-center">
              <span className="text-3xl mr-4">{platformIcons[platformName]}</span>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{platformName} Management</h1>
                <p className="text-gray-600">{accounts.length} accounts configured</p>
              </div>
            </div>
          </div>
          <button
            onClick={() => setShowAddAccount(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Account
          </button>
        </div>
      </div>

      {/* Accounts List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Accounts</h2>
        </div>
        
        {accounts.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-500">No accounts configured yet</p>
            <button
              onClick={() => setShowAddAccount(true)}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              Add your first account
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {accounts.map((account) => (
              <div key={account.name} className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {account.authenticated ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-500" />
                      )}
                      <span className="font-medium text-gray-900">{account.name}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        account.active 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {account.active ? 'Active' : 'Inactive'}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        account.authenticated 
                          ? 'bg-blue-100 text-blue-700' 
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {account.authenticated ? 'Authenticated' : 'Not Authenticated'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        setSelectedAccount(account);
                        setShowContentGenerator(true);
                      }}
                      className="flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors text-sm"
                    >
                      <FileVideo className="h-4 w-4 mr-1" />
                      Generate
                    </button>
                    
                    <button
                      onClick={() => handleUploadContent(account.name)}
                      className="flex items-center px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm"
                    >
                      <Upload className="h-4 w-4 mr-1" />
                      Upload
                    </button>
                    
                    <button
                      onClick={() => openAccountEditor(account)}
                      className="flex items-center px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                    >
                      <Edit className="h-4 w-4 mr-1" />
                      Edit
                    </button>
                    
                    <button
                      onClick={() => handleDeleteAccount(account.name)}
                      className="flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm"
                    >
                      <Trash2 className="h-4 w-4 mr-1" />
                      Delete
                    </button>
                  </div>
                </div>
                
                {account.description && (
                  <p className="mt-2 text-sm text-gray-600">{account.description}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Active Tasks */}
      {Object.keys(activeTasks).length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Active Tasks</h2>
          </div>
          <div className="p-6 space-y-4">
            {Object.entries(activeTasks).map(([taskId, task]) => (
              <div key={taskId} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">Task {taskId.split('_').pop()}</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    task.status === 'completed' ? 'bg-green-100 text-green-700' :
                    task.status === 'failed' ? 'bg-red-100 text-red-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {task.status}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${task.progress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">{task.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Account Modal */}
      {showAddAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Add New {platformName} Account</h3>
              <button
                onClick={() => {
                  setShowAddAccount(false);
                  setAuthData({});
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Basic Account Info */}
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Basic Information</h4>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Account Name *
                  </label>
                  <input
                    type="text"
                    value={accountForm.name}
                    onChange={(e) => setAccountForm(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter a unique name for this account"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <input
                    type="text"
                    value={accountForm.description}
                    onChange={(e) => setAccountForm(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Optional description for this account"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={accountForm.tags}
                    onChange={(e) => setAccountForm(prev => ({ ...prev, tags: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="gaming, entertainment, music"
                  />
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="active"
                    checked={accountForm.active}
                    onChange={(e) => setAccountForm(prev => ({ ...prev, active: e.target.checked }))}
                    className="mr-2"
                  />
                  <label htmlFor="active" className="text-sm text-gray-700">
                    Account Active
                  </label>
                </div>
              </div>

              {/* Platform-specific Authentication */}
              <div className="border-t pt-6">
                <PlatformAuthForm 
                  platform={platformName} 
                  onAuthDataChange={setAuthData}
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-8 pt-6 border-t">
              <button
                onClick={() => {
                  setShowAddAccount(false);
                  setAuthData({});
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAddAccount}
                disabled={!accountForm.name || (platformName === 'YouTube' && !authData.client_secrets_content) || (platformName === 'TikTok' && (!authData.client_key || !authData.client_secret))}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Create & Authenticate Account
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Content Generator Modal */}
      {showContentGenerator && selectedAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Generate Content</h3>
              <button
                onClick={() => setShowContentGenerator(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="flex space-x-4">
                <button
                  onClick={() => setContentForm(prev => ({ ...prev, type: 'url' }))}
                  className={`flex-1 p-3 rounded-lg border-2 ${
                    contentForm.type === 'url' 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200'
                  }`}
                >
                  <LinkIcon className="h-5 w-5 mx-auto mb-2" />
                  <span className="text-sm">From URL</span>
                </button>
                
                <button
                  onClick={() => setContentForm(prev => ({ ...prev, type: 'file' }))}
                  className={`flex-1 p-3 rounded-lg border-2 ${
                    contentForm.type === 'file' 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200'
                  }`}
                >
                  <FileVideo className="h-5 w-5 mx-auto mb-2" />
                  <span className="text-sm">From File</span>
                </button>
              </div>
              
              {contentForm.type === 'url' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    YouTube URL
                  </label>
                  <input
                    type="url"
                    value={contentForm.url}
                    onChange={(e) => setContentForm(prev => ({ ...prev, url: e.target.value }))}
                    placeholder="https://www.youtube.com/watch?v=..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Video File
                  </label>
                  <div
                    {...getRootProps()}
                    className={`w-full p-6 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
                      isDragActive 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <input {...getInputProps()} />
                    {contentForm.file ? (
                      <div className="text-center">
                        <FileVideo className="h-8 w-8 mx-auto mb-2 text-green-500" />
                        <p className="text-sm text-gray-600">{contentForm.file.name}</p>
                      </div>
                    ) : (
                      <div className="text-center">
                        <Upload className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                        <p className="text-sm text-gray-600">
                          Drop a video file here or click to select
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowContentGenerator(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerateContent}
                disabled={contentForm.type === 'url' ? !contentForm.url : !contentForm.file}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Generate Clips
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PlatformDetail;