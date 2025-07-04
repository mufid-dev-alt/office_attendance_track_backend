# 🏢 Office Attendance Management API

## 📋 Project Overview

This is a comprehensive FastAPI-based attendance management system designed for modern office environments. The API provides a lightweight, database-free solution that maintains all data in memory, making it ideal for small to medium-sized teams and demonstration purposes.

## ✨ Core Features

The system offers the following capabilities:
- 🔐 **Authentication System** - Secure login for both employees and administrators
- 📊 **Attendance Tracking** - Complete attendance recording and history management
- 👥 **User Management** - Comprehensive employee data management
- ✅ **Task Management** - Integrated todo system for personal productivity
- 📈 **Data Export** - Clean CSV export functionality for attendance records

## 🚀 Quick Start Guide

### 📧 Authentication Credentials

The system comes pre-configured with the following test accounts:

**🔑 Administrator Account:**
- Email: `admin@company.com`
- Password: `admin123`
- Privileges: Full system access and user management

**👤 Employee Accounts:**
- `user1@company.com` / `user123` (User One)
- `user2@company.com` / `user123` (User Two)  
- `user3@company.com` / `user123` (User Three)
- `user4@company.com` / `user123` (User Four)
- `user5@company.com` / `user123` (User Five)

### 📊 Pre-loaded Data

The system includes comprehensive sample data for June 2025, featuring:
- 📅 **20+ working days** of attendance records per employee
- 📈 **Realistic attendance patterns** (approximately 85% attendance rate)
- 🚫 **Weekend exclusion** - No attendance records for Saturday/Sunday
- 🎯 **Varied patterns** - Each employee has unique attendance behavior

## 🛠 API Documentation

### 🔐 Authentication Endpoints
- `GET/POST /api/login` - Employee and administrator authentication
- `GET /api/logout` - Secure session termination

### 👥 User Management
- `GET /api/users` - Retrieve all system users (Admin access required)

### 📅 Attendance Management
- `GET /api/attendance` - Retrieve attendance records (supports user filtering)
- `POST /api/attendance` - Record daily attendance
- `GET /api/attendance/stats` - Generate attendance statistics and reports

### ✅ Task Management
- `GET /api/todos` - Retrieve user task lists
- `POST /api/todos` - Create new tasks
- `PUT /api/todos/{id}` - Update task status
- `DELETE /api/todos/{id}` - Remove completed tasks

### 🔍 System Health
- `GET /` - System information and statistics overview
- `GET /health` - Application health status
- `GET /api/test` - Connectivity verification

## 💻 Local Development

### Prerequisites
Ensure you have Python 3.7+ installed on your system.

### Installation & Setup

```bash
# 📦 Install required dependencies
pip install -r requirements.txt

# 🚀 Launch development server
python dev-start.py

# Alternative: Direct uvicorn execution
uvicorn main:app --reload --port 8000
```

The API will be accessible at `http://localhost:8000`

## 🌐 Production Deployment

### Vercel Integration
This application is optimized for Vercel deployment with zero-configuration setup:

1. 📋 Connect your GitHub repository to Vercel
2. 🔄 Automatic deployment pipeline activation
3. 📝 Configuration handled via `vercel.json`

## 🏗 Technical Architecture

### Technology Stack
- 🚀 **FastAPI** - Modern, high-performance web framework
- 📝 **Pydantic** - Data validation and API documentation
- ⚡ **Uvicorn** - Lightning-fast ASGI server
- 🐍 **Python** - Reliable, enterprise-grade programming language

### Design Philosophy
The in-memory data approach was selected for several strategic reasons:
- 🎯 **Simplicity** - Zero database configuration requirements
- ⚡ **Performance** - Optimal response times and throughput
- 🎭 **Demo-Ready** - Perfect for presentations and proof-of-concepts
- ☁️ **Serverless Compatible** - Seamless integration with modern hosting platforms

### Production Considerations
For enterprise deployments with larger user bases, consider integrating:
- 🗄️ PostgreSQL or MySQL database
- 🔒 Advanced authentication systems
- 📊 Analytics and reporting modules
- 🔄 Data backup and recovery solutions

## 📄 License & Usage

This project is designed for educational and small business applications. The codebase demonstrates modern API development practices and can serve as a foundation for larger enterprise systems.

---

**🏢 Built for DCM Infotech** - Streamlining office attendance management with modern technology solutions. 