# Office Attendance Tracker Backend

FastAPI backend for Office Attendance Tracker with MongoDB Atlas integration.

## Deployment

This application is configured for deployment on Vercel with MongoDB Atlas as the database.

### Environment Variables

Set the following environment variable in your Vercel project settings:

```
MONGODB_URI=mongodb+srv://office-app-user:admin123@office-attendance-track.hml0x1v.mongodb.net/?retryWrites=true&w=majority&appName=Office-attendance-track
```

## API Endpoints

- `/api/users` - User management
- `/api/attendance` - Attendance records
- `/api/todos` - Todo items
- `/api/login` - Authentication 