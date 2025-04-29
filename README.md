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

## Prerequisites

Before you begin, ensure you have the following installed:
- Docker and Docker Compose
- Git
- Python 3.8+ (for local development)
- Node.js 14+ (for local development)

## Quick Start with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/amuyakkala/mvpbeta.git
   cd mvpbeta
   ```

2. Create necessary directories:
   ```bash
   mkdir -p data
   ```

3. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Local Development Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the backend server:
   ```bash
   python run.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start the development server:
   ```bash
   npm start
   ```

## Default Credentials

- Email: admin@test.com
- Password: password123

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