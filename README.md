# Office Attendance Tracker Backend

FastAPI backend for Office Attendance Tracker with MongoDB Atlas integration.

## Deployment

This application is configured for deployment on Render with MongoDB Atlas as the database.

### Environment Variables

Set the following environment variables in your Render project settings:

```
MONGODB_URI=mongodb+srv://office-app-user:admin123@office-attendance-track.hml0x1v.mongodb.net/?retryWrites=true&w=majority&appName=Office-attendance-track
ENVIRONMENT=production
```

### Deployment Instructions

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## API Endpoints

- `/api/users` - User management
- `/api/attendance` - Attendance records
- `/api/todos` - Todo items
- `/api/login` - Authentication