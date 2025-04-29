# EchosysAI MVP

A fully working MVP that lets users upload traces/logs, automatically run Root Cause Analysis (RCA), create and manage incidents/issues, and maintain an audit trail.

## Features

- User authentication and authorization
- Trace/log upload and analysis
- Root Cause Analysis (RCA) engine
- Issue tracking and management
- Real-time notifications
- Audit logging
- Health monitoring

## System Architecture

```
[Frontend (React SprintBoard UI)]  <-->  [Backend API Server (FastAPI)]  <-->  [SQLite Database]
```

### Components

- **Frontend**: React-based SprintBoard UI
- **Backend**: FastAPI server
- **Database**: SQLite
- **Authentication**: JWT-based
- **Notification System**: Real-time notifications with database persistence
- **Audit Logging**: Comprehensive action tracking

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- Docker and Docker Compose (optional)

### Local Development

1. Clone the repository
2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   python run.py
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Edit .env with your configuration
   npm start
   ```

### Docker Deployment

```bash
docker-compose up -d
```

## API Documentation

Access the Swagger UI at `http://localhost:8000/docs` when the backend is running.

### Notification System

The notification system provides real-time updates for various events:

- New issues created
- Issue status changes
- Trace analysis results
- System alerts

Endpoints:
- `GET /notifications` - Get user notifications
- `POST /notifications/read` - Mark notifications as read
- `DELETE /notifications` - Clear notifications
- `GET /notifications/health` - Health check

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Health Checks

- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000/health`

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure SQLite database file exists
   - Check database permissions
   - Verify DATABASE_URL in .env

2. **Authentication Issues**
   - Verify JWT_SECRET_KEY in .env
   - Check token expiration
   - Ensure proper headers in API requests

3. **Notification Service Issues**
   - Check database connection
   - Verify notification settings in .env
   - Monitor health check endpoint

### Dummy Credentials

- Email: admin@test.com
- Password: password123

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 

mkdir -p data 

docker-compose ps 