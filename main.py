from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta
import json
import os

app = FastAPI(title="Office Attendance Management API", version="1.0.0")

# Configure CORS properly for production
origins = [
    "https://office-attendance-track-frontend.vercel.app",
    "https://office-attendance-track-backend.vercel.app", 
    "http://localhost:3000",
    "http://localhost:3001",
    "*"  # Allow all origins - can be restricted in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Pydantic models for request/response
class LoginRequest(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: int
    email: str
    full_name: str
    role: str

class LoginResponse(BaseModel):
    success: bool
    user: Optional[User] = None
    message: Optional[str] = None

class AttendanceRequest(BaseModel):
    user_id: int
    status: str
    date: str
    notes: Optional[str] = None

class AttendanceRecord(BaseModel):
    id: int
    user_id: int
    status: str
    date: str
    notes: Optional[str] = None

class TodoRequest(BaseModel):
    user_id: int
    notes: str
    date_created: Optional[str] = None

class Todo(BaseModel):
    id: int
    user_id: int
    notes: str
    date_created: str

class CreateUserRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: Optional[str] = "user"

# Data persistence functions
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.json")
TODOS_FILE = os.path.join(DATA_DIR, "todos.json")
DELETED_USERS_FILE = os.path.join(DATA_DIR, "deleted_users.json")

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_data_from_file(file_path, default_data):
    """Load data from JSON file or return default if file doesn't exist"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return default_data
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return default_data

def save_data_to_file(file_path, data):
    """Save data to JSON file"""
    try:
        ensure_data_directory()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(data)} records to {file_path}")
    except Exception as e:
        print(f"Error saving {file_path}: {e}")

def save_users():
    """Save users to file"""
    save_data_to_file(USERS_FILE, USERS)

def save_attendance():
    """Save attendance records to file"""
    save_data_to_file(ATTENDANCE_FILE, ATTENDANCE_RECORDS)

def save_todos():
    """Save todos to file"""
    save_data_to_file(TODOS_FILE, TODOS)

def save_deleted_users():
    """Save deleted users to file"""
    save_data_to_file(DELETED_USERS_FILE, DELETED_USERS)

# Default data for demonstration
DEFAULT_USERS = [
    {
        "id": 1,
        "email": "admin@company.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin"
    },
    {
        "id": 2,
        "email": "user1@company.com",
        "password": "user123",
        "full_name": "User One",
        "role": "user"
    },
    {
        "id": 3,
        "email": "user2@company.com",
        "password": "user123",
        "full_name": "User Two",
        "role": "user"
    },
    {
        "id": 4,
        "email": "user3@company.com",
        "password": "user123",
        "full_name": "User Three",
        "role": "user"
    },
    {
        "id": 5,
        "email": "user4@company.com",
        "password": "user123",
        "full_name": "User Four",
        "role": "user"
    },
    {
        "id": 6,
        "email": "user5@company.com",
        "password": "user123",
        "full_name": "User Five",
        "role": "user"
    }
]

# Global state management for Vercel serverless environment
class GlobalState:
    def __init__(self):
        self.users = DEFAULT_USERS.copy()
        self.attendance_records = self.generate_attendance_data()
        self.todos = []
        self.deleted_users = []
        print(f"🚀 Initialized global state with {len(self.users)} users and {len(self.attendance_records)} attendance records")
    
    def generate_attendance_data(self):
        """Generate default attendance data"""
        attendance_records = []
        record_id = 1
        
        # Start from April 1, 2025
        start_date = datetime(2025, 4, 1)
        # End at July 2, 2025
        end_date = datetime(2025, 7, 2)
        
        for user in DEFAULT_USERS[1:]:  # Skip admin user
            current_date = start_date
            while current_date <= end_date:
                # Skip weekends (Saturday=5, Sunday=6)
                if current_date.weekday() < 5:
                    # Random attendance pattern (85% present, 15% absent)
                    status = "present" if random.random() < 0.85 else "absent"
                    
                    attendance_records.append({
                        "id": record_id,
                        "user_id": user["id"],
                        "status": status,
                        "date": current_date.strftime("%Y-%m-%d"),
                        "notes": None
                    })
                    record_id += 1
                
                current_date += timedelta(days=1)
        
        return attendance_records

# Initialize global state
state = GlobalState()

# Compatibility aliases for existing code
USERS = state.users
ATTENDANCE_RECORDS = state.attendance_records
TODOS = state.todos
DELETED_USERS = state.deleted_users

# Note: System reset removed - all users created by admin will persist permanently

@app.get("/")
def read_root():
    return {
        "message": "Office Attendance Management API", 
        "version": "1.0.0", 
        "status": "running",
        "total_users": len(state.users),
        "total_attendance_records": len(state.attendance_records),
        "environment": "serverless",
        "note": "Data persists within session only (Vercel serverless limitation)",
        "endpoints": {
            "login": "/api/login",
            "users": "/api/users",
            "attendance": "/api/attendance",
            "todos": "/api/todos"
        }
    }

@app.get("/api/test")
def test_endpoint():
    return {"message": "API is working correctly", "status": "success"}

@app.options("/api/login")
def login_options():
    return {"message": "CORS preflight OK"}

@app.get("/api/login")
def login_get(email: str, password: str):
    """Login endpoint using GET method with query parameters"""
    try:
        user = next((u for u in USERS if u["email"] == email and u["password"] == password), None)
        
        if user:
            return LoginResponse(
                success=True,
                user=User(
                    id=user["id"],
                    email=user["email"],
                    full_name=user["full_name"],
                    role=user["role"]
                )
            )
        else:
            return LoginResponse(
                success=False,
                message="Invalid credentials"
            )
    except Exception as e:
        return LoginResponse(
            success=False,
            message=f"Login error: {str(e)}"
        )

@app.post("/api/login")
def login_post(login_data: LoginRequest):
    """Login endpoint using POST method"""
    try:
        user = next((u for u in USERS if u["email"] == login_data.email and u["password"] == login_data.password), None)
        
        if user:
            return LoginResponse(
                success=True,
                user=User(
                    id=user["id"],
                    email=user["email"],
                    full_name=user["full_name"],
                    role=user["role"]
                )
            )
        else:
            return LoginResponse(
                success=False,
                message="Invalid credentials"
            )
    except Exception as e:
        return LoginResponse(
            success=False,
            message=f"Login error: {str(e)}"
        )

@app.options("/api/users")
def users_options():
    """Handle CORS preflight for users endpoint"""
    return {"message": "OK"}

@app.get("/api/users")
def get_users():
    """Get all users (admin only)"""
    return [
        {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "created_at": user.get("created_at", None)
        }
        for user in USERS
    ]

@app.post("/api/users")
def create_user(user_data: CreateUserRequest):
    """Create a new user"""
    global USERS
    
    # Check if email already exists
    existing_user = next((u for u in USERS if u["email"] == user_data.email), None)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Auto-generate user ID
    max_id = max([u["id"] for u in USERS], default=0)
    new_user_id = max_id + 1
    
    new_user = {
        "id": new_user_id,
        "email": user_data.email,
        "password": user_data.password,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "created_at": datetime.now().isoformat()
    }
    USERS.append(new_user)
    
    # Save to file for persistence
    save_users()
    
    return {
        "id": new_user["id"],
        "email": new_user["email"],
        "full_name": new_user["full_name"],
        "role": new_user["role"],
        "created_at": new_user["created_at"]
    }

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    """Delete a user and all their data"""
    global USERS, ATTENDANCE_RECORDS, TODOS, DELETED_USERS
    
    # Find the user
    user_to_delete = next((u for u in USERS if u["id"] == user_id), None)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting admin users
    if user_to_delete["role"] == "admin":
        raise HTTPException(status_code=403, detail="Cannot delete admin users")
    
    # Store user data for undo functionality
    user_attendance = [r for r in ATTENDANCE_RECORDS if r["user_id"] == user_id]
    user_todos = [t for t in TODOS if t["user_id"] == user_id]
    
    deleted_user_data = {
        "user": user_to_delete,
        "attendance": user_attendance,
        "todos": user_todos,
        "deleted_at": datetime.now().isoformat()
    }
    DELETED_USERS.append(deleted_user_data)
    
    # Remove user from USERS
    USERS = [u for u in USERS if u["id"] != user_id]
    
    # Remove all attendance records
    ATTENDANCE_RECORDS = [r for r in ATTENDANCE_RECORDS if r["user_id"] != user_id]
    
    # Remove all todos
    TODOS = [t for t in TODOS if t["user_id"] != user_id]
    
    # Save all changes to files
    save_users()
    save_attendance()
    save_todos()
    save_deleted_users()
    
    return {
        "message": f"User {user_to_delete['full_name']} and all their data has been deleted",
        "deleted_user": {
            "id": user_to_delete["id"],
            "full_name": user_to_delete["full_name"],
            "email": user_to_delete["email"]
        },
        "undo_available": True
    }

@app.post("/api/users/{user_id}/undo")
def undo_user_deletion(user_id: int):
    """Undo user deletion and restore all their data"""
    global USERS, ATTENDANCE_RECORDS, TODOS, DELETED_USERS
    
    # Find the deleted user
    deleted_user_data = next((d for d in DELETED_USERS if d["user"]["id"] == user_id), None)
    if not deleted_user_data:
        raise HTTPException(status_code=404, detail="No deleted user found to undo")
    
    # Restore user
    USERS.append(deleted_user_data["user"])
    
    # Restore attendance records
    ATTENDANCE_RECORDS.extend(deleted_user_data["attendance"])
    
    # Restore todos
    TODOS.extend(deleted_user_data["todos"])
    
    # Remove from deleted users list
    DELETED_USERS = [d for d in DELETED_USERS if d["user"]["id"] != user_id]
    
    # Save all changes to files
    save_users()
    save_attendance()
    save_todos()
    save_deleted_users()
    
    return {
        "message": f"User {deleted_user_data['user']['full_name']} and all their data has been restored",
        "restored_user": {
            "id": deleted_user_data["user"]["id"],
            "full_name": deleted_user_data["user"]["full_name"],
            "email": deleted_user_data["user"]["email"]
        }
    }

@app.get("/api/attendance")
def get_attendance(
    user_id: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    """Get attendance records - optionally filtered by user_id, month, and year"""
    records = ATTENDANCE_RECORDS
    
    # Filter by user_id
    if user_id:
        records = [record for record in records if record.get("user_id") == user_id]
    
    # Filter by month and year
    if month is not None or year is not None:
        filtered_records = []
        for record in records:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
            if year is not None and record_date.year != year:
                continue
            if month is not None and record_date.month != month:
                continue
            filtered_records.append(record)
        records = filtered_records
    
    # For export purposes, remove notes and clean up data
    clean_records = []
    for record in records:
        clean_record = {
            "id": record["id"],
            "user_id": record["user_id"],
            "status": record["status"],
            "date": record["date"]
        }
        # Add user name for better export
        user = next((u for u in USERS if u["id"] == record["user_id"]), None)
        if user:
            clean_record["user_name"] = user["full_name"]
            clean_record["user_email"] = user["email"]
        
        clean_records.append(clean_record)
    
    return clean_records

@app.post("/api/attendance")
def create_attendance(record: AttendanceRequest):
    """Create attendance record"""
    global ATTENDANCE_RECORDS
    
    # Check if attendance already exists for this user and date
    existing_record = next(
        (r for r in ATTENDANCE_RECORDS 
         if r["user_id"] == record.user_id and r["date"] == record.date),
        None
    )
    
    if existing_record:
        # Update existing record
        existing_record["status"] = record.status
        existing_record["notes"] = record.notes
        # Save to file for persistence
        save_attendance()
        return existing_record
    
    # Create new record
    new_record = {
        "id": len(ATTENDANCE_RECORDS) + 1,
        "user_id": record.user_id,
        "status": record.status,
        "date": record.date,
        "notes": record.notes
    }
    ATTENDANCE_RECORDS.append(new_record)
    
    # Save to file for persistence
    save_attendance()
    
    # Return the complete record with user info for frontend
    user = next((u for u in USERS if u["id"] == record.user_id), None)
    if user:
        new_record["user_name"] = user["full_name"]
        new_record["user_email"] = user["email"]
    
    return new_record

@app.delete("/api/attendance/{attendance_id}")
def delete_attendance(attendance_id: int):
    """Delete an attendance record (for undo functionality)"""
    global ATTENDANCE_RECORDS
    for i, record in enumerate(ATTENDANCE_RECORDS):
        if record["id"] == attendance_id:
            deleted_record = ATTENDANCE_RECORDS.pop(i)
            # Save to file for persistence
            save_attendance()
            return {"message": "Attendance deleted", "record": deleted_record}
    raise HTTPException(status_code=404, detail="Attendance record not found")

@app.get("/api/attendance/stats")
def get_attendance_stats(
    user_id: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    """Get attendance statistics - optionally filtered by user_id, month, and year"""
    records = ATTENDANCE_RECORDS
    
    # Filter by user_id
    if user_id:
        records = [record for record in records if record.get("user_id") == user_id]
    
    # Filter by month and year
    if month is not None or year is not None:
        filtered_records = []
        for record in records:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
            if year is not None and record_date.year != year:
                continue
            if month is not None and record_date.month != month:
                continue
            filtered_records.append(record)
        records = filtered_records
    
    total_records = len(records)
    present_count = len([r for r in records if r.get("status") == "present"])
    
    return {
        "total_days": total_records,
        "present_days": present_count,
        "absent_days": total_records - present_count,
        "attendance_rate": (present_count / total_records * 100) if total_records > 0 else 0
    }

@app.get("/api/todos")
def get_todos(user_id: Optional[int] = Query(None)):
    """Get todos - optionally filtered by user_id"""
    if user_id:
        return [todo for todo in TODOS if todo.get("user_id") == user_id]
    return TODOS

@app.post("/api/todos")
def create_todo(todo: TodoRequest):
    """Create a new todo"""
    new_todo = {
        "id": len(TODOS) + 1,
        "user_id": todo.user_id,
        "notes": todo.notes,
        "date_created": todo.date_created or datetime.now().strftime("%Y-%m-%d")
    }
    TODOS.append(new_todo)
    
    # Save to file for persistence
    save_todos()
    
    return new_todo

@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, notes: Optional[str] = Query(None)):
    """Update a todo"""
    for i, existing_todo in enumerate(TODOS):
        if existing_todo["id"] == todo_id:
            if notes is not None:
                TODOS[i]["notes"] = notes
            # Save to file for persistence
            save_todos()
            return TODOS[i]
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    """Delete a todo"""
    for i, todo in enumerate(TODOS):
        if todo["id"] == todo_id:
            deleted_todo = TODOS.pop(i)
            # Save to file for persistence
            save_todos()
            return {"message": "Todo deleted", "todo": deleted_todo}
    raise HTTPException(status_code=404, detail="Todo not found")

@app.get("/api/logout")
def logout():
    """Logout endpoint"""
    return {"success": True, "message": "Logged out successfully"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "office-attendance-api"} 