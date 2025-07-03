from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta

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

# Mock data for demonstration
USERS = [
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

# Pre-populate attendance data for April 1, 2025 to July 2, 2025 (excluding weekends)
def generate_attendance_data():
    attendance_records = []
    record_id = 1
    
    # Start from April 1, 2025
    start_date = datetime(2025, 4, 1)
    # End at July 2, 2025
    end_date = datetime(2025, 7, 2)
    
    for user in USERS[1:]:  # Skip admin user
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

ATTENDANCE_RECORDS = generate_attendance_data()
TODOS = []

@app.get("/")
def read_root():
    return {
        "message": "Office Attendance Management API", 
        "version": "1.0.0", 
        "status": "running",
        "total_users": len(USERS),
        "total_attendance_records": len(ATTENDANCE_RECORDS),
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

@app.get("/api/users")
def get_users():
    """Get all users (admin only)"""
    return [
        {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
        for user in USERS
    ]

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
    return new_todo

@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, notes: Optional[str] = Query(None)):
    """Update a todo"""
    for i, existing_todo in enumerate(TODOS):
        if existing_todo["id"] == todo_id:
            if notes is not None:
                TODOS[i]["notes"] = notes
            return TODOS[i]
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    """Delete a todo"""
    for i, todo in enumerate(TODOS):
        if todo["id"] == todo_id:
            deleted_todo = TODOS.pop(i)
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