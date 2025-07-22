# Social Media Automation - Web Application

Professional web-based social media automation suite with multi-platform support.

## 🚀 Features

- **Multi-Platform Support**: YouTube, TikTok, Instagram, Twitter
- **Modern Web Interface**: React.js frontend with Tailwind CSS
- **Professional Backend**: FastAPI with JWT authentication
- **Real-time Analytics**: Performance metrics and activity monitoring
- **Email Notifications**: Mailjet integration for alerts
- **Backup System**: Automated configuration backup/restore
- **Security Features**: IP whitelisting, session management
- **Performance Monitoring**: System resource tracking

## 📁 Project Structure

```
SocialMediaAutomation/
├── web_app/
│   ├── backend/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Pydantic models
│   │   ├── settings_manager.py  # Settings & backup management
│   │   ├── scheduler.py         # Task scheduling
│   │   ├── auth.py             # Authentication
│   │   └── requirements.txt    # Backend dependencies
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── components/     # React components
│   │   │   ├── pages/         # Main pages
│   │   │   ├── contexts/      # React contexts
│   │   │   └── services/      # API services
│   │   ├── package.json       # Frontend dependencies
│   │   └── tailwind.config.js # Styling configuration
│   └── start_server.py        # Application launcher
├── core/
│   ├── youtube_automation.py   # YouTube API integration
│   ├── tiktok_api.py          # TikTok API integration
│   ├── tiktok_automation.py   # TikTok automation
│   └── tiktok_automation_enhanced.py
├── config/
│   └── config.json            # Application configuration
└── requirements.txt           # Main dependencies
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -r web_app/backend/requirements.txt

# Configure environment
cp config/config.json.example config/config.json
```

### Frontend Setup
```bash
cd web_app/frontend
npm install
npm run build
```

## 🚀 Running the Application

### Start the Web Application
```bash
python web_app/start_server.py
```

### Development Mode
```bash
# Backend (FastAPI)
cd web_app/backend
uvicorn main:app --reload --port 8000

# Frontend (React)
cd web_app/frontend  
npm start
```

## 🔧 Configuration

### 1. Google OAuth (YouTube)
- Create project in Google Cloud Console
- Enable YouTube Data API v3
- Download client secrets JSON
- Upload via web interface

### 2. TikTok API
- Register TikTok Developer Account
- Get API keys and secrets
- Configure in web interface

### 3. Email Notifications (Mailjet)
- Create Mailjet account
- Get API key and secret key
- Configure in Settings page

### 4. Database
- File-based configuration (JSON)
- Automatic backup system
- Import/export functionality

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Platforms
- `GET /api/platforms` - List all platforms
- `POST /api/platforms/{platform}/accounts` - Create account
- `GET /api/platforms/{platform}/accounts` - List accounts

### Analytics
- `GET /api/analytics/dashboard` - Dashboard metrics
- `GET /api/analytics/activity` - Activity log

### Settings
- `GET/POST /api/settings` - Manage settings
- `POST /api/settings/backup` - Create backup
- `POST /api/settings/restore` - Restore backup

## 🔒 Security Features

- JWT token authentication
- IP address whitelisting
- Session timeout management
- Password strength validation
- Secure API key storage

## 📧 Email Notifications

Automated notifications for:
- Upload success/failure
- System maintenance alerts  
- Weekly performance reports
- Security alerts

## 🔄 Backup System

- Automated configuration backups
- ZIP-based archive format
- Configurable retention policies
- One-click restore functionality

## 🎯 Platform Support

### YouTube
- OAuth2 authentication
- Video upload automation
- Analytics tracking
- Bulk operations

### TikTok  
- API key authentication
- Content scheduling
- Performance metrics
- Automated posting

### Instagram & Twitter
- Coming soon with API integration

## 📱 Web Interface

- **Dashboard**: Overview and quick actions
- **Platforms**: Account management
- **Analytics**: Performance metrics
- **Activity**: Real-time monitoring  
- **Settings**: Complete configuration

## 🚀 Production Deployment

### Using Docker (Recommended)
```bash
# Build and run
docker-compose up -d
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Build frontend
cd web_app/frontend && npm run build

# Start production server
python web_app/start_server.py --prod
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and support, please create an issue in the repository.