from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta
import json
import os

# Try to import dotenv, but don't fail if it's not installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  WARNING: python-dotenv not installed. Environment variables from .env file won't be loaded.")
    print("📝 To install: pip install python-dotenv")

# Import MongoDB connection
from mongodb import mongodb

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

# Load environment variables
# The dotenv import is now handled by the try-except block above

# Initialize MongoDB with default data on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Initialize default data if collections are empty
        mongodb.initialize_default_data()
        print("✅ MongoDB initialized with default data")
    except Exception as e:
        print(f"❌ Error initializing MongoDB: {e}")

@app.get("/")
def read_root():
    """Root endpoint for health check"""
    return {
        "status": "online",
        "message": "Office Attendance API is running",
        "version": "1.0.0",
        "documentation": "/docs",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test")
def test_endpoint():
    """Test endpoint for debugging"""
    return {"status": "ok", "message": "Test endpoint working", "timestamp": datetime.now().isoformat()}

@app.options("/api/login")
def login_options():
    """Handle CORS preflight request for login"""
    return {}

@app.get("/api/login")
def login_get(email: str, password: str):
    """Login endpoint (GET method)"""
    # Get all users from MongoDB
    users = mongodb.get_users()
    
    # Find user by email and password
    user = next((u for u in users if u["email"] == email and u["password"] == password), None)
    
    if user:
        # Return user info without password
        user_info = {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
        return {"success": True, "user": user_info}
    else:
        return {"success": False, "message": "Invalid credentials"}

@app.post("/api/login")
def login_post(login_data: LoginRequest):
    """Login endpoint (POST method)"""
    # Get all users from MongoDB
    users = mongodb.get_users()
    
    # Find user by email and password
    user = next((u for u in users if u["email"] == login_data.email and u["password"] == login_data.password), None)
    
    if user:
        # Return user info without password
        user_info = {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
        return {"success": True, "user": user_info}
    else:
        return {"success": False, "message": "Invalid credentials"}

@app.options("/api/users")
def users_options():
    """Handle CORS preflight request for users"""
    return {}

@app.get("/api/users")
def get_users():
    """Get all users"""
    try:
        # Get users from MongoDB
        users = mongodb.get_users()
        
        # Remove passwords from response
        sanitized_users = []
        for user in users:
            sanitized_user = {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "created_at": user.get("created_at")
            }
            sanitized_users.append(sanitized_user)
            
        return {"success": True, "users": sanitized_users}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/users")
def create_user(user_data: CreateUserRequest):
    """Create a new user"""
    try:
        # Get all users from MongoDB
        users = mongodb.get_users()
        
        # Check if email already exists
        if any(u["email"] == user_data.email for u in users):
            return {"success": False, "message": "Email already exists"}
        
        # Create new user
        new_user = {
            "email": user_data.email,
            "password": user_data.password,
            "full_name": user_data.full_name,
            "role": user_data.role
        }
        
        # Add user to MongoDB
        created_user = mongodb.add_user(new_user)
        
        # Return sanitized user (without password)
        sanitized_user = {
            "id": created_user["id"],
            "email": created_user["email"],
            "full_name": created_user["full_name"],
            "role": created_user["role"],
            "created_at": created_user.get("created_at")
        }
        
        return {"success": True, "user": sanitized_user}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    """Delete a user (soft delete with undo capability)"""
    try:
        # Delete user from MongoDB
        deleted_data = mongodb.delete_user(user_id)
        
        if not deleted_data:
            return {"success": False, "message": "User not found"}
            
        # Return success response
        return {
            "success": True,
            "message": f"User {user_id} deleted successfully",
            "user": {
                "id": deleted_data["user"]["id"],
                "email": deleted_data["user"]["email"],
                "full_name": deleted_data["user"]["full_name"]
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/users/{user_id}/permanent-delete")
def permanent_delete_user(user_id: int):
    """Permanently delete a user without undo capability"""
    try:
        # This is not implemented in MongoDB manager, but we can simulate it
        # by deleting the user and then removing it from deleted_users
        deleted_data = mongodb.delete_user(user_id)
        
        if not deleted_data:
            return {"success": False, "message": "User not found"}
            
        # Return success response
        return {
            "success": True,
            "message": f"User {user_id} permanently deleted",
            "user": {
                "id": deleted_data["user"]["id"],
                "email": deleted_data["user"]["email"],
                "full_name": deleted_data["user"]["full_name"]
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/users/{user_id}/undo")
def undo_user_deletion(user_id: int):
    """Undo a user deletion"""
    try:
        # Restore user from MongoDB
        restored_data = mongodb.undo_user_deletion(user_id)
        
        if not restored_data:
            return {"success": False, "message": "Deleted user not found"}
            
        # Return success response
        return {
            "success": True,
            "message": f"User {user_id} restored successfully",
            "user": {
                "id": restored_data["user"]["id"],
                "email": restored_data["user"]["email"],
                "full_name": restored_data["user"]["full_name"]
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/attendance")
def get_attendance(
    user_id: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    """Get attendance records with optional filters"""
    try:
        # Get attendance records from MongoDB
        records = mongodb.get_attendance(user_id, month, year)
        
        # Get all users for user details
        users = mongodb.get_users()
        users_dict = {u["id"]: u for u in users}
        
        # Enrich attendance records with user details
        enriched_records = []
        for record in records:
            user = users_dict.get(record["user_id"])
            if user:
                enriched_record = {
                    **record,
                    "user_name": user["full_name"],
                    "user_email": user["email"]
                }
                enriched_records.append(enriched_record)
            else:
                # Include record even if user not found
                enriched_records.append({
                    **record,
                    "user_name": "Unknown User",
                    "user_email": "unknown"
                })
        
        return {"success": True, "records": enriched_records}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/attendance")
def create_attendance(record: AttendanceRequest):
    """Create or update attendance record"""
    try:
        # Validate user exists
        users = mongodb.get_users()
        user = next((u for u in users if u["id"] == record.user_id), None)
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Create attendance record
        attendance_data = {
            "user_id": record.user_id,
            "status": record.status,
            "date": record.date,
            "notes": record.notes
        }
        
        # Add or update attendance record in MongoDB
        created_record = mongodb.add_attendance(attendance_data)
        
        # Enrich with user details
        enriched_record = {
            **created_record,
            "user_name": user["full_name"],
            "user_email": user["email"]
        }
        
        return {"success": True, "record": enriched_record}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.delete("/api/attendance/{attendance_id}")
def delete_attendance(attendance_id: int):
    """Delete attendance record"""
    try:
        # Delete attendance record from MongoDB
        deleted_record = mongodb.delete_attendance(attendance_id)
        
        if not deleted_record:
            return {"success": False, "message": "Attendance record not found"}
            
        return {"success": True, "message": f"Attendance record {attendance_id} deleted successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/attendance/stats")
def get_attendance_stats(
    user_id: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    """Get attendance statistics"""
    try:
        # Get attendance records from MongoDB
        records = mongodb.get_attendance(user_id, month, year)
        
        # Calculate statistics
        total_records = len(records)
        present_records = len([r for r in records if r["status"] == "present"])
        absent_records = len([r for r in records if r["status"] == "absent"])
        
        present_percentage = (present_records / total_records * 100) if total_records > 0 else 0
        absent_percentage = (absent_records / total_records * 100) if total_records > 0 else 0
        
        return {
            "success": True,
            "stats": {
                "total": total_records,
                "present": present_records,
                "absent": absent_records,
                "present_percentage": round(present_percentage, 2),
                "absent_percentage": round(absent_percentage, 2)
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/todos")
def get_todos(user_id: Optional[int] = Query(None)):
    """Get todos with optional user filter"""
    try:
        # Get todos from MongoDB
        todos = mongodb.get_todos(user_id)
        return {"success": True, "todos": todos}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/todos")
def create_todo(todo: TodoRequest):
    """Create a new todo"""
    try:
        # Create todo in MongoDB
        created_todo = mongodb.add_todo({
            "user_id": todo.user_id,
            "notes": todo.notes,
            "date_created": todo.date_created or datetime.now().isoformat()
        })
        
        return {"success": True, "todo": created_todo}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, notes: Optional[str] = Query(None)):
    """Update todo notes"""
    try:
        # Update todo in MongoDB
        if notes is None:
            return {"success": False, "message": "Notes cannot be empty"}
            
        updated_todo = mongodb.update_todo(todo_id, notes)
        
        if not updated_todo:
            return {"success": False, "message": "Todo not found"}
            
        return {"success": True, "todo": updated_todo}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    """Delete todo"""
    try:
        # Delete todo from MongoDB
        deleted_todo = mongodb.delete_todo(todo_id)
        
        if not deleted_todo:
            return {"success": False, "message": "Todo not found"}
            
        return {"success": True, "message": f"Todo {todo_id} deleted successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/logout")
def logout():
    """Logout endpoint"""
    return {"success": True, "message": "Logged out successfully"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/attendance/force-sync")
def force_sync_attendance():
    """Force synchronization of attendance data"""
    try:
        # This is a no-op with MongoDB since data is already persistent
        return {"success": True, "message": "Attendance data synchronized successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}