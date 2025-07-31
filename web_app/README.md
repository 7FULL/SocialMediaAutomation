# Social Media Automation Suite v2.0

A modern, professional web application for automating social media content across multiple platforms.

## Features

### 🎯 Core Features
- **Multi-Platform Support**: YouTube, TikTok, Instagram, Twitter
- **Account Management**: Multiple accounts per platform
- **Content Scheduling**: Advanced scheduling with weekly patterns
- **Automated Uploads**: Background upload processing
- **Content Generation**: Generate clips from URLs or uploaded files
- **Real-time Monitoring**: Live task progress tracking

### 🔐 Security Features
- **JWT Authentication**: Secure token-based authentication
- **Session Management**: Automatic token refresh and validation
- **API Security**: Protected endpoints with proper authorization
- **Input Validation**: Comprehensive data validation

### 🎨 User Interface
- **Modern Design**: Clean, professional interface with Tailwind CSS
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live status updates and progress tracking
- **Intuitive Navigation**: Easy-to-use sidebar and routing

### 🚀 Technical Features
- **FastAPI Backend**: High-performance async API
- **React Frontend**: Modern single-page application
- **Background Tasks**: Asynchronous content processing
- **File Upload Support**: Drag-and-drop file uploads
- **Progress Tracking**: Real-time task monitoring

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Quick Start
1. Clone the repository
2. Navigate to the web_app directory
3. Run the start script:
   ```bash
   python start_server.py
   ```

This will automatically:
- Install backend dependencies
- Install frontend dependencies
- Start both servers
- Open the application in your browser

### Manual Installation

#### Backend Setup
```bash
cd web_app/backend
pip install -r requirements.txt
python main.py
```

#### Frontend Setup
```bash
cd web_app/frontend
npm install
npm start
```

## Usage

### Login
- **Username**: admin
- **Password**: admin123

### Dashboard
- View system statistics
- Monitor platform status
- Track recent activity

### Platform Management
- Enable/disable auto-upload for each platform
- View account counts and status
- Navigate to detailed platform settings

### Account Management
- Add new social media accounts
- Configure account settings
- Manage authentication tokens
- Set up posting schedules

### Content Generation
- Generate clips from YouTube URLs
- Upload and process video files
- Monitor generation progress
- Manage content libraries

## API Documentation

The API documentation is available at:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Configuration

### Environment Variables
- `REACT_APP_API_URL`: Frontend API URL (default: http://localhost:8000/api)
- `JWT_SECRET_KEY`: JWT signing secret (change in production)

### Authentication
The application uses JWT tokens for authentication. In production, make sure to:
1. Change the JWT secret key
2. Use strong passwords
3. Enable HTTPS
4. Configure proper CORS settings

## Development

### Backend Development
```bash
cd web_app/backend
uvicorn main:app --reload --port 8000
```

### Frontend Development
```bash
cd web_app/frontend
npm start
```

### Building for Production
```bash
cd web_app/frontend
npm run build
```

## Architecture

### Backend (FastAPI)
- **main.py**: Main application entry point
- **models.py**: Pydantic data models
- **auth.py**: Authentication utilities
- **scheduler.py**: Background task scheduler

### Frontend (React)
- **contexts/**: React context providers
- **components/**: Reusable UI components
- **pages/**: Application pages/routes
- **services/**: API service layer

## Security Considerations

### Production Deployment
1. Change default credentials
2. Use environment variables for secrets
3. Enable HTTPS
4. Configure proper CORS settings
5. Set up rate limiting
6. Enable logging and monitoring

### API Security
- All endpoints require authentication
- JWT tokens with expiration
- Input validation and sanitization
- Proper error handling

## Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Python version (3.8+)
   - Install missing dependencies
   - Verify port 8000 is available

2. **Frontend won't start**
   - Check Node.js version (16+)
   - Run `npm install` in frontend directory
   - Clear npm cache if needed

3. **Authentication errors**
   - Clear browser localStorage
   - Check JWT secret key configuration
   - Verify API endpoints are accessible

### Support
For issues and questions, please check the troubleshooting guide or create an issue in the repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.