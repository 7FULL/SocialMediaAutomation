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
    reauthenticateAccount,
    generateClipsFromUrl,
    generateClipsFromFile,
    uploadContent,
    getTaskStatus,
    getSchedulerStatus,
    getNextUploadTimes
  } = useApi();

  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [showAccountEditor, setShowAccountEditor] = useState(false);
  const [showReauth, setShowReauth] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [showContentGenerator, setShowContentGenerator] = useState(false);
  const [activeTasks, setActiveTasks] = useState({});
  const [isGeneratingClips, setIsGeneratingClips] = useState(false);
  const [newTimeInputs, setNewTimeInputs] = useState({});
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [nextUploads, setNextUploads] = useState({});

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
    type: 'url', // 'url' or 'file'
    mobileFormat: true
  });

  const [authData, setAuthData] = useState({});
  const [reauthData, setReauthData] = useState({});

  const platformIcons = {
    'YouTube': '🎥',
    'TikTok': '🎵',
    'Instagram': '📸',
    'Twitter': '🐦'
  };

  useEffect(() => {
    loadAccounts();
    loadSchedulerInfo();
  }, [platformName]);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const data = await getAccounts(platformName);
      console.log('Loaded accounts data:', data); // Debug log
      setAccounts(data);
    } catch (error) {
      console.error('Error loading accounts:', error); // Debug log
      toast.error('Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  const loadSchedulerInfo = async () => {
    try {
      const [statusData, uploadsData] = await Promise.all([
        getSchedulerStatus(platformName),
        getNextUploadTimes(platformName)
      ]);
      setSchedulerStatus(statusData);
      setNextUploads(uploadsData);
    } catch (error) {
      console.error('Error loading scheduler info:', error);
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
      loadSchedulerInfo();
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
      loadSchedulerInfo();
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
        loadSchedulerInfo();
      } catch (error) {
        toast.error('Failed to delete account');
      }
    }
  };

  const handleReauthenticate = async () => {
    try {
      const response = await reauthenticateAccount(platformName, selectedAccount.name, reauthData);
      
      if (response.success && response.authenticated) {
        toast.success(`Account re-authenticated successfully! ${response.auth_message}`);
      } else {
        toast.error(`Re-authentication failed: ${response.auth_message}`);
      }
      
      setShowReauth(false);
      setSelectedAccount(null);
      setReauthData({});
      loadAccounts();
      loadSchedulerInfo();
    } catch (error) {
      toast.error('Failed to re-authenticate account');
    }
  };

  const handleGenerateContent = async () => {
    try {
      setIsGeneratingClips(true);
      
      let response;
      if (contentForm.type === 'url') {
        response = await generateClipsFromUrl(platformName, selectedAccount.name, contentForm.url, contentForm.mobileFormat);
      } else {
        response = await generateClipsFromFile(platformName, selectedAccount.name, contentForm.file, contentForm.mobileFormat);
      }
      
      const taskId = response.task_id;
      setActiveTasks(prev => ({ ...prev, [taskId]: { status: 'processing', progress: 0 } }));
      
      const formatType = contentForm.mobileFormat ? 'mobile (9:16)' : 'original';
      toast.success(`Clip generation started in ${formatType} format! This may take a few minutes...`);
      setShowContentGenerator(false);
      setContentForm({ url: '', file: null, type: 'url', mobileFormat: true });
      
      // Poll for task status
      pollTaskStatus(taskId);
    } catch (error) {
      toast.error('Failed to start content generation');
      setIsGeneratingClips(false);
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
          toast.success(status.message || 'Clips generated successfully!');
          clearInterval(pollInterval);
          setActiveTasks(prev => {
            const newTasks = { ...prev };
            delete newTasks[taskId];
            return newTasks;
          });
          setIsGeneratingClips(false);
          // Refresh accounts to update clips count
          loadAccounts();
        } else if (status.status === 'failed') {
          toast.error(status.message || 'Task failed');
          clearInterval(pollInterval);
          setActiveTasks(prev => {
            const newTasks = { ...prev };
            delete newTasks[taskId];
            return newTasks;
          });
          setIsGeneratingClips(false);
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
      // Clear the input after adding
      setNewTimeInputs(prev => ({
        ...prev,
        [day]: ''
      }));
    }
  };
  
  const handleAddTime = (day) => {
    const time = newTimeInputs[day];
    if (time) {
      addScheduleTime(day, time);
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
          <div className="flex space-x-3">
            <button
              onClick={() => {
                loadAccounts();
                loadSchedulerInfo();
              }}
              className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              title="Refresh account and scheduler data"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </button>
            <button
              onClick={() => setShowAddAccount(true)}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Account
            </button>
          </div>
        </div>
      </div>

      {/* Scheduler Status */}
      {schedulerStatus && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                <Clock className="h-5 w-5 mr-2" />
                Scheduler Status
              </h2>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${schedulerStatus.is_running ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                <span className={`text-sm font-medium ${schedulerStatus.is_running ? 'text-green-700' : 'text-gray-500'}`}>
                  {schedulerStatus.is_running ? 'Running' : 'Stopped'}
                </span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(nextUploads).map(([accountName, uploadInfo]) => (
                <div key={accountName} className={`p-4 rounded-lg border-2 ${
                  uploadInfo.active 
                    ? uploadInfo.time_remaining === 'Ready to upload' 
                      ? 'border-orange-200 bg-orange-50'
                      : 'border-green-200 bg-green-50'
                    : 'border-gray-200 bg-gray-50'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{accountName}</h4>
                    <div className={`w-2 h-2 rounded-full ${
                      uploadInfo.active 
                        ? uploadInfo.time_remaining === 'Ready to upload'
                          ? 'bg-orange-500'
                          : 'bg-green-500'
                        : 'bg-gray-400'
                    }`}></div>
                  </div>
                  
                  {uploadInfo.active ? (
                    <>
                      {uploadInfo.next_upload && (
                        <p className="text-sm text-gray-600 mb-1">
                          Next: {new Date(uploadInfo.next_upload).toLocaleString()}
                        </p>
                      )}
                      <p className={`text-sm font-medium ${
                        uploadInfo.time_remaining === 'Ready to upload' 
                          ? 'text-orange-600' 
                          : 'text-green-600'
                      }`}>
                        {uploadInfo.time_remaining || 'No schedule set'}
                      </p>
                    </>
                  ) : (
                    <p className="text-sm text-gray-500">Account inactive</p>
                  )}
                </div>
              ))}
            </div>
            
            {Object.keys(nextUploads).length === 0 && (
              <div className="text-center py-8">
                <Clock className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No accounts configured</p>
              </div>
            )}
          </div>
        </div>
      )}

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
                      
                      {/* Content Status Badge */}
                      {account.clips_stats && account.clips_stats.clips_per_week > 0 && (
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          account.clips_stats.status === 'healthy' ? 'bg-green-100 text-green-700' :
                          account.clips_stats.status === 'low' ? 'bg-yellow-100 text-yellow-700' : 
                          'bg-red-100 text-red-700'
                        }`}>
                          {account.clips_stats.status === 'healthy' ? 'Content Ready' :
                           account.clips_stats.status === 'low' ? 'Low Content' : 'Critical'}
                        </span>
                      )}
                    </div>
                    
                    {/* Clips Statistics */}
                    {account.clips_stats && (
                      <div className="flex items-center space-x-4 mt-2 text-sm" title="Content availability statistics based on upload schedule">
                        <div className="flex items-center space-x-1">
                          <FileVideo className="h-4 w-4 text-gray-500" />
                          <span className="text-gray-700">
                            <span className="font-medium">{account.clips_stats.available_clips}</span> clips available
                          </span>
                        </div>
                        
                        {account.clips_stats.clips_per_week > 0 && (
                          <>
                            <div className="text-gray-400">•</div>
                            <div className="flex items-center space-x-1">
                              <Calendar className="h-4 w-4 text-gray-500" />
                              <span className="text-gray-700">
                                <span className="font-medium">{account.clips_stats.clips_per_week}</span> needed/week
                              </span>
                            </div>
                            
                            <div className="text-gray-400">•</div>
                            <div className="flex items-center space-x-2">
                              <Clock className="h-4 w-4 text-gray-500" />
                              <span className={`font-medium ${
                                account.clips_stats.status === 'healthy' ? 'text-green-600' :
                                account.clips_stats.status === 'low' ? 'text-yellow-600' : 'text-red-600'
                              }`}>
                                {account.clips_stats.weeks_of_content} weeks
                              </span>
                              
                              {/* Progress Bar */}
                              <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full transition-all duration-300 ${
                                    account.clips_stats.status === 'healthy' ? 'bg-green-500' :
                                    account.clips_stats.status === 'low' ? 'bg-yellow-500' : 'bg-red-500'
                                  }`}
                                  style={{
                                    width: `${Math.min(100, (account.clips_stats.weeks_of_content / 4) * 100)}%`
                                  }}
                                />
                              </div>
                            </div>
                          </>
                        )}
                      </div>
                    )}
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
                      onClick={() => {
                        setSelectedAccount(account);
                        setReauthData({});
                        setShowReauth(true);
                      }}
                      className="flex items-center px-3 py-1 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors text-sm"
                    >
                      <RefreshCw className="h-4 w-4 mr-1" />
                      Re-auth
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

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Default Video Title (optional)
                  </label>
                  <input
                    type="text"
                    value={accountForm.title}
                    onChange={(e) => setAccountForm(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter default title for videos"
                  />
                  <p className="text-xs text-gray-500 mt-1">Leave empty for auto-generated titles</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    YouTube Category
                  </label>
                  <select
                    value={accountForm.category_id}
                    onChange={(e) => setAccountForm(prev => ({ ...prev, category_id: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select a category</option>
                    <option value="1">Film & Animation</option>
                    <option value="2">Autos & Vehicles</option>
                    <option value="10">Music</option>
                    <option value="15">Pets & Animals</option>
                    <option value="17">Sports</option>
                    <option value="19">Travel & Events</option>
                    <option value="20">Gaming</option>
                    <option value="22">People & Blogs</option>
                    <option value="23">Comedy</option>
                    <option value="24">Entertainment</option>
                    <option value="25">News & Politics</option>
                    <option value="26">Howto & Style</option>
                    <option value="27">Education</option>
                    <option value="28">Science & Technology</option>
                    <option value="29">Nonprofits & Activism</option>
                  </select>
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
            
            {/* Mobile Format Options */}
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  id="mobileFormat"
                  checked={contentForm.mobileFormat}
                  onChange={(e) => setContentForm(prev => ({ ...prev, mobileFormat: e.target.checked }))}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div className="flex-1">
                  <label htmlFor="mobileFormat" className="block text-sm font-medium text-gray-900">
                    Create mobile-optimized clips (9:16)
                  </label>
                  <p className="text-xs text-gray-600 mt-1">
                    Perfect for YouTube Shorts, TikTok, and Instagram Reels. Clips will be automatically cropped and resized to vertical format.
                  </p>
                </div>
              </div>
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
                disabled={(contentForm.type === 'url' ? !contentForm.url : !contentForm.file) || isGeneratingClips}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
              >
                {isGeneratingClips && (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                )}
                {isGeneratingClips ? 'Generating Clips...' : 'Generate Clips'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Account Editor Modal */}
      {showAccountEditor && selectedAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-900">
                  Edit Account: {selectedAccount.name}
                </h2>
                <button
                  onClick={() => setShowAccountEditor(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {/* Account Details */}
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Account Name
                  </label>
                  <input
                    type="text"
                    value={selectedAccount.name}
                    onChange={(e) => setSelectedAccount({...selectedAccount, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={selectedAccount.description || ''}
                    onChange={(e) => setSelectedAccount({...selectedAccount, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="3"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tags
                    </label>
                    <input
                      type="text"
                      value={selectedAccount.tags || ''}
                      onChange={(e) => setSelectedAccount({...selectedAccount, tags: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="comedy, entertainment, viral"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Clip Duration (seconds)
                    </label>
                    <input
                      type="number"
                      min="30"
                      max="60"
                      value={selectedAccount.clip_duration || 57}
                      onChange={(e) => setSelectedAccount({...selectedAccount, clip_duration: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* Video Configuration Section */}
                <div className="border-t pt-6">
                  <h4 className="text-md font-semibold text-gray-900 mb-4">Video Configuration</h4>
                  <div className="grid grid-cols-1 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Default Video Title
                      </label>
                      <input
                        type="text"
                        value={selectedAccount.title || ''}
                        onChange={(e) => setSelectedAccount({...selectedAccount, title: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter default title for videos (leave empty for auto-generated)"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        This will be the default title for uploaded videos. Leave empty to use auto-generated titles.
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        YouTube Category ID
                      </label>
                      <select
                        value={selectedAccount.category_id || ''}
                        onChange={(e) => setSelectedAccount({...selectedAccount, category_id: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select a category</option>
                        <option value="1">Film & Animation</option>
                        <option value="2">Autos & Vehicles</option>
                        <option value="10">Music</option>
                        <option value="15">Pets & Animals</option>
                        <option value="17">Sports</option>
                        <option value="19">Travel & Events</option>
                        <option value="20">Gaming</option>
                        <option value="22">People & Blogs</option>
                        <option value="23">Comedy</option>
                        <option value="24">Entertainment</option>
                        <option value="25">News & Politics</option>
                        <option value="26">Howto & Style</option>
                        <option value="27">Education</option>
                        <option value="28">Science & Technology</option>
                        <option value="29">Nonprofits & Activism</option>
                      </select>
                      <p className="text-xs text-gray-500 mt-1">
                        Choose the appropriate YouTube category for your videos. This helps with discoverability.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedAccount.active}
                    onChange={(e) => setSelectedAccount({...selectedAccount, active: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-900">
                    Account Active
                  </label>
                </div>
              </div>

              {/* Schedule Section */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Schedule</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.keys(scheduleForm).map(day => (
                    <div key={day} className="p-4 border border-gray-200 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-2">{day}</h4>
                      <div className="space-y-2">
                        {scheduleForm[day].map((time, index) => (
                          <div key={index} className="flex items-center justify-between bg-gray-50 px-2 py-1 rounded">
                            <span className="text-sm">{time}</span>
                            <button
                              onClick={() => removeScheduleTime(day, time)}
                              className="text-red-500 hover:text-red-700"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                        <div className="flex items-center space-x-2">
                          <input
                            type="time"
                            value={newTimeInputs[day] || ''}
                            onChange={(e) => setNewTimeInputs(prev => ({...prev, [day]: e.target.value}))}
                            className="text-sm border border-gray-300 rounded px-2 py-1 flex-1"
                            placeholder="Select time"
                          />
                          <button
                            onClick={() => handleAddTime(day)}
                            disabled={!newTimeInputs[day]}
                            className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Add
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-3 mt-6 pt-6 border-t">
                <button
                  onClick={() => setShowAccountEditor(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateAccount}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Re-authentication Modal */}
      {showReauth && selectedAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Re-authenticate {platformName} Account</h3>
              <button
                onClick={() => {
                  setShowReauth(false);
                  setReauthData({});
                  setSelectedAccount(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center">
                <RefreshCw className="h-5 w-5 text-blue-500 mr-2" />
                <div>
                  <p className="font-medium text-blue-900">Re-authenticate: {selectedAccount.name}</p>
                  <p className="text-sm text-blue-700 mt-1">
                    Update the authentication credentials for this account. This will not change any other account settings.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-6">
              {/* Platform-specific Authentication */}
              <div>
                <PlatformAuthForm 
                  platform={platformName} 
                  onAuthDataChange={setReauthData}
                  isReauth={true}
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-8 pt-6 border-t">
              <button
                onClick={() => {
                  setShowReauth(false);
                  setReauthData({});
                  setSelectedAccount(null);
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleReauthenticate}
                disabled={
                  (platformName === 'YouTube' && !reauthData.use_existing_credentials && !reauthData.client_secrets_content) || 
                  (platformName === 'TikTok' && (!reauthData.client_key || !reauthData.client_secret)) ||
                  (platformName === 'Instagram' && !reauthData.access_token) ||
                  (platformName === 'Twitter' && (!reauthData.api_key || !reauthData.api_secret || !reauthData.access_token_key || !reauthData.access_token_secret))
                }
                className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Re-authenticate Account
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PlatformDetail;