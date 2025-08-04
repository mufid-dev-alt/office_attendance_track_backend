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

# Configure CORS to allow frontend access
origins = [
    "https://office-attendance-track-frontend.onrender.com",
    "https://office-attendance-track-backend.onrender.com", 
    "http://localhost:3000",
    "http://localhost:3001",
    "*"  # Allow all origins for now to fix connectivity issues
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins to fix 502 issues
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
    role: str  # Added role to the login request

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
        # Don't let MongoDB errors crash the app startup
        print("⚠️ App will continue running without database initialization")

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

@app.get("/api/health")
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "attendance-api", "timestamp": datetime.now().isoformat()}

@app.options("/api/login")
def login_options():
    """Handle CORS preflight request for login"""
    return {}

@app.get("/api/login")
def login_get(email: str, password: str):
    """Login endpoint (GET method)"""
    print("Received request for /api/login (GET)")
    try:
        # Get all users from MongoDB
        users = mongodb.get_users()
        
        if not users:
            print("⚠️ Warning: No users found in database")
            return {"success": False, "message": "Authentication service unavailable. Please try again later."}
        
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
            print(f"✅ User {user['email']} logged in successfully (GET method)")
            return {"success": True, "user": user_info}
        else:
            print(f"❌ Failed login attempt for email: {email} (GET method)")
            return {"success": False, "message": "Invalid email or password"}
    except Exception as e:
        print(f"❌ Error during login (GET method): {e}")
        return {"success": False, "message": "An error occurred during login. Please try again later."}

@app.post("/api/login")
def login_post(login_data: LoginRequest):
    """Login endpoint (POST method)"""
    print("Received request for /api/login (POST)")
    try:
        # Get all users from MongoDB
        users = mongodb.get_users()
        
        if not users:
            print("⚠️ Warning: No users found in database")
            return {"success": False, "message": "Authentication service unavailable. Please try again later."}
        
        # Find user by email and password
        user = next((u for u in users if u["email"] == login_data.email and u["password"] == login_data.password), None)
        
        if user:
            # Check if the role matches
            if user["role"] != login_data.role:
                if login_data.role == "admin":
                    return {"success": False, "message": "You are not an admin. Please use user login section."}
                else:
                    return {"success": False, "message": "You are an admin. Please use admin login section."}
            # Return user info without password
            user_info = {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
            print(f"✅ User {user['email']} logged in successfully")
            return {"success": True, "user": user_info}
        else:
            print(f"❌ Failed login attempt for email: {login_data.email}")
            return {"success": False, "message": "Invalid email or password"}
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return {"success": False, "message": "An error occurred during login. Please try again later."}

@app.options("/api/users")
def users_options():
    """Handle CORS preflight request for users"""
    return {}

@app.get("/api/users")
def get_users():
    """Get all users"""
    print("Received request for /api/users")
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
        print(f"❌ Error creating user: {e}")
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
        # First check if user exists in active users
        user_data = mongodb.get_user_by_id(user_id)
        if user_data:
            # User is active, delete them normally
            deleted_data = mongodb.delete_user(user_id)
            if not deleted_data:
                return {"success": False, "message": "User not found"}
        else:
            # User might be in deleted_users collection, check there
            deleted_user_data = mongodb.get_deleted_user_by_id(user_id)
            if not deleted_user_data:
                return {"success": False, "message": "User not found"}
            
            # Remove from deleted_users collection permanently
            mongodb.permanently_remove_deleted_user(user_id)
            deleted_data = {"user": deleted_user_data["user"]}
            
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

@app.options("/api/attendance")
def attendance_options():
    """Handle CORS preflight request for attendance"""
    return {}

@app.get("/api/attendance")
def get_attendance(
    user_id: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    """Get attendance records with optional filters"""
    try:
        records = mongodb.get_attendance(user_id, month, year)
        return {"success": True, "records": records}
    except Exception as e:
        print(f"❌ Error getting attendance records: {e}")
        return {"success": False, "message": str(e)}

@app.post("/api/attendance")
def create_attendance(record: AttendanceRequest):
    """Create a new attendance record"""
    try:
        # Add attendance record to MongoDB
        created_record = mongodb.add_attendance({
            "user_id": record.user_id,
            "status": record.status,
            "date": record.date,
            "notes": record.notes
        })
        
        return {"success": True, "record": created_record}
    except Exception as e:
        print(f"❌ Error creating attendance record: {e}")
        return {"success": False, "message": str(e)}

@app.delete("/api/attendance/{attendance_id}")
def delete_attendance(attendance_id: int):
    """Delete an attendance record"""
    try:
        deleted_record = mongodb.delete_attendance(attendance_id)
        if not deleted_record:
            return {"success": False, "message": "Attendance record not found"}
        return {"success": True, "record": deleted_record}
    except Exception as e:
        print(f"❌ Error deleting attendance record: {e}")
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
            "present_days": present_records,
            "absent_days": absent_records,
            "total_days": total_records,
            "present_percentage": round(present_percentage, 2),
            "absent_percentage": round(absent_percentage, 2)
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.options("/api/todos")
def todos_options():
    """Handle CORS preflight request for todos"""
    return {}

@app.get("/api/todos")
def get_todos(user_id: Optional[int] = Query(None)):
    """Get todos for a specific user or all todos"""
    try:
        todos = mongodb.get_todos(user_id)
        return {"success": True, "todos": todos}
    except Exception as e:
        print(f"❌ Error getting todos: {e}")
        return {"success": False, "message": str(e)}

@app.post("/api/todos")
def create_todo(todo: TodoRequest):
    """Create a new todo"""
    try:
        # Add todo to MongoDB
        created_todo = mongodb.add_todo({
            "user_id": todo.user_id,
            "notes": todo.notes,
            "date_created": todo.date_created or datetime.now().isoformat()
        })
        
        return {"success": True, "todo": created_todo}
    except Exception as e:
        print(f"❌ Error creating todo: {e}")
        return {"success": False, "message": str(e)}

@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, notes: Optional[str] = Query(None)):
    """Update a todo's notes"""
    try:
        if notes is None:
            return {"success": False, "message": "Notes cannot be empty"}
        updated_todo = mongodb.update_todo(todo_id, notes)
        if not updated_todo:
            return {"success": False, "message": "Todo not found"}
        return {"success": True, "todo": updated_todo}
    except Exception as e:
        print(f"❌ Error updating todo: {e}")
        return {"success": False, "message": str(e)}

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    """Delete a todo"""
    try:
        deleted_todo = mongodb.delete_todo(todo_id)
        if not deleted_todo:
            return {"success": False, "message": "Todo not found"}
        return {"success": True, "todo": deleted_todo}
    except Exception as e:
        print(f"❌ Error deleting todo: {e}")
        return {"success": False, "message": str(e)}

@app.get("/api/logout")
def logout():
    """Logout endpoint"""
    return {"success": True, "message": "Logged out successfully"}



@app.post("/api/attendance/force-sync")
def force_sync_attendance():
    """Force synchronization of attendance data"""
    try:
        # Get total record count for response
        all_records = mongodb.get_attendance()
        record_count = len(all_records)
        return {"success": True, "message": "Attendance data synchronized successfully", "record_count": record_count}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/ping")
def ping():
    print("/ping endpoint hit")
    return {"message": "pong"}

# Add this for Render deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
