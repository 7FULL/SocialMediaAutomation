import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Key, FileText, Eye, EyeOff, Info } from 'lucide-react';

function PlatformAuthForm({ platform, onAuthDataChange }) {
  const [showSecrets, setShowSecrets] = useState({});
  const [authData, setAuthData] = useState({});

  const handleInputChange = (field, value) => {
    const newAuthData = { ...authData, [field]: value };
    setAuthData(newAuthData);
    onAuthDataChange(newAuthData);
  };

  const toggleSecretVisibility = (field) => {
    setShowSecrets(prev => ({ ...prev, [field]: !prev[field] }));
  };

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target.result;
        handleInputChange('client_secrets_content', content);
      };
      reader.readAsText(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json']
    },
    maxFiles: 1
  });

  const renderYouTubeForm = () => (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <Info className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900">YouTube Setup Instructions</h4>
            <p className="text-sm text-blue-700 mt-1">
              1. Go to <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer" className="underline">Google Cloud Console</a>
              <br />
              2. Create a new project or select existing one
              <br />
              3. Enable YouTube Data API v3
              <br />
              4. Create credentials (OAuth 2.0 Client ID)
              <br />
              5. Download the client secrets JSON file
            </p>
          </div>
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Client Secrets File
        </label>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            isDragActive 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="h-8 w-8 mx-auto mb-2 text-gray-400" />
          {authData.client_secrets_content ? (
            <div>
              <p className="text-sm text-green-600 font-medium">Client secrets file loaded ✓</p>
              <p className="text-xs text-gray-500 mt-1">File contains the OAuth 2.0 credentials</p>
            </div>
          ) : (
            <div>
              <p className="text-sm text-gray-600">Drop client secrets JSON file here or click to select</p>
              <p className="text-xs text-gray-500 mt-1">Must be a valid Google OAuth 2.0 client secrets file</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderTikTokForm = () => (
    <div className="space-y-4">
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex items-start">
          <Info className="h-5 w-5 text-purple-600 mr-2 mt-0.5" />
          <div>
            <h4 className="font-medium text-purple-900">TikTok Setup Instructions</h4>
            <p className="text-sm text-purple-700 mt-1">
              1. Go to <a href="https://developers.tiktok.com/" target="_blank" rel="noopener noreferrer" className="underline">TikTok Developers</a>
              <br />
              2. Create a new app or select existing one
              <br />
              3. Get your Client Key and Client Secret
              <br />
              4. Configure redirect URLs and permissions
            </p>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Client Key
        </label>
        <div className="relative">
          <input
            type={showSecrets.client_key ? 'text' : 'password'}
            value={authData.client_key || ''}
            onChange={(e) => handleInputChange('client_key', e.target.value)}
            className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Enter your TikTok Client Key"
          />
          <button
            type="button"
            onClick={() => toggleSecretVisibility('client_key')}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            {showSecrets.client_key ? (
              <EyeOff className="h-5 w-5 text-gray-400" />
            ) : (
              <Eye className="h-5 w-5 text-gray-400" />
            )}
          </button>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Client Secret
        </label>
        <div className="relative">
          <input
            type={showSecrets.client_secret ? 'text' : 'password'}
            value={authData.client_secret || ''}
            onChange={(e) => handleInputChange('client_secret', e.target.value)}
            className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Enter your TikTok Client Secret"
          />
          <button
            type="button"
            onClick={() => toggleSecretVisibility('client_secret')}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            {showSecrets.client_secret ? (
              <EyeOff className="h-5 w-5 text-gray-400" />
            ) : (
              <Eye className="h-5 w-5 text-gray-400" />
            )}
          </button>
        </div>
      </div>
    </div>
  );

  const renderInstagramForm = () => (
    <div className="space-y-4">
      <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
        <div className="flex items-start">
          <Info className="h-5 w-5 text-pink-600 mr-2 mt-0.5" />
          <div>
            <h4 className="font-medium text-pink-900">Instagram Setup Instructions</h4>
            <p className="text-sm text-pink-700 mt-1">
              1. Go to <a href="https://developers.facebook.com/" target="_blank" rel="noopener noreferrer" className="underline">Facebook Developers</a>
              <br />
              2. Create a new app with Instagram Basic Display
              <br />
              3. Get your access token
              <br />
              4. Configure Instagram Basic Display settings
            </p>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Access Token
        </label>
        <div className="relative">
          <input
            type={showSecrets.access_token ? 'text' : 'password'}
            value={authData.access_token || ''}
            onChange={(e) => handleInputChange('access_token', e.target.value)}
            className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
            placeholder="Enter your Instagram Access Token"
          />
          <button
            type="button"
            onClick={() => toggleSecretVisibility('access_token')}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            {showSecrets.access_token ? (
              <EyeOff className="h-5 w-5 text-gray-400" />
            ) : (
              <Eye className="h-5 w-5 text-gray-400" />
            )}
          </button>
        </div>
      </div>
    </div>
  );

  const renderTwitterForm = () => (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <Info className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900">Twitter Setup Instructions</h4>
            <p className="text-sm text-blue-700 mt-1">
              1. Go to <a href="https://developer.twitter.com/" target="_blank" rel="noopener noreferrer" className="underline">Twitter Developer Portal</a>
              <br />
              2. Create a new app or select existing one
              <br />
              3. Get your API keys and tokens
              <br />
              4. Configure app permissions and settings
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            API Key
          </label>
          <div className="relative">
            <input
              type={showSecrets.api_key ? 'text' : 'password'}
              value={authData.api_key || ''}
              onChange={(e) => handleInputChange('api_key', e.target.value)}
              className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="API Key"
            />
            <button
              type="button"
              onClick={() => toggleSecretVisibility('api_key')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {showSecrets.api_key ? (
                <EyeOff className="h-4 w-4 text-gray-400" />
              ) : (
                <Eye className="h-4 w-4 text-gray-400" />
              )}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            API Secret
          </label>
          <div className="relative">
            <input
              type={showSecrets.api_secret ? 'text' : 'password'}
              value={authData.api_secret || ''}
              onChange={(e) => handleInputChange('api_secret', e.target.value)}
              className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="API Secret"
            />
            <button
              type="button"
              onClick={() => toggleSecretVisibility('api_secret')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {showSecrets.api_secret ? (
                <EyeOff className="h-4 w-4 text-gray-400" />
              ) : (
                <Eye className="h-4 w-4 text-gray-400" />
              )}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Access Token
          </label>
          <div className="relative">
            <input
              type={showSecrets.access_token_key ? 'text' : 'password'}
              value={authData.access_token_key || ''}
              onChange={(e) => handleInputChange('access_token_key', e.target.value)}
              className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Access Token"
            />
            <button
              type="button"
              onClick={() => toggleSecretVisibility('access_token_key')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {showSecrets.access_token_key ? (
                <EyeOff className="h-4 w-4 text-gray-400" />
              ) : (
                <Eye className="h-4 w-4 text-gray-400" />
              )}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Access Token Secret
          </label>
          <div className="relative">
            <input
              type={showSecrets.access_token_secret ? 'text' : 'password'}
              value={authData.access_token_secret || ''}
              onChange={(e) => handleInputChange('access_token_secret', e.target.value)}
              className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Access Token Secret"
            />
            <button
              type="button"
              onClick={() => toggleSecretVisibility('access_token_secret')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {showSecrets.access_token_secret ? (
                <EyeOff className="h-4 w-4 text-gray-400" />
              ) : (
                <Eye className="h-4 w-4 text-gray-400" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPlatformForm = () => {
    switch (platform) {
      case 'YouTube':
        return renderYouTubeForm();
      case 'TikTok':
        return renderTikTokForm();
      case 'Instagram':
        return renderInstagramForm();
      case 'Twitter':
        return renderTwitterForm();
      default:
        return (
          <div className="text-center py-8">
            <p className="text-gray-500">Authentication form not available for {platform}</p>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
          <Key className="h-5 w-5 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{platform} Authentication</h3>
          <p className="text-sm text-gray-600">Configure your {platform} API credentials</p>
        </div>
      </div>

      {renderPlatformForm()}
    </div>
  );
}

export default PlatformAuthForm;