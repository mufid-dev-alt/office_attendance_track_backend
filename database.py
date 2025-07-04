import json
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

class SimpleDatabase:
    """Simple database abstraction that works with Vercel serverless environment"""
    
    def __init__(self):
        self.data = {
            'users': [],
            'attendance': [],
            'todos': [],
            'deleted_users': []
        }
        self.load_data()
    
    def load_data(self):
        """Load data from environment variables or use defaults"""
        try:
            # Always start with default data for demo purposes
            # In production, you'd load from a real database
            self.data['users'] = self.get_default_users()
            self.data['attendance'] = self.generate_default_attendance()
            self.data['todos'] = []
            self.data['deleted_users'] = []
                
            print(f"✅ Database loaded: {len(self.data['users'])} users, {len(self.data['attendance'])} attendance records")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.data = {
                'users': self.get_default_users(),
                'attendance': self.generate_default_attendance(),
                'todos': [],
                'deleted_users': []
            }
    
    def save_data(self):
        """Save data (in memory for serverless environment)"""
        try:
            print(f"💾 Data saved in memory: {len(self.data['users'])} users")
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def get_default_users(self) -> List[Dict]:
        """Get default user data"""
        return [
            {
                "id": 1,
                "email": "admin@company.com",
                "password": "admin123",
                "full_name": "Admin User",
                "role": "admin",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": 2,
                "email": "user1@company.com",
                "password": "user123",
                "full_name": "User One",
                "role": "user",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": 3,
                "email": "user2@company.com",
                "password": "user123",
                "full_name": "User Two",
                "role": "user",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": 4,
                "email": "user3@company.com",
                "password": "user123",
                "full_name": "User Three",
                "role": "user",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": 5,
                "email": "user4@company.com",
                "password": "user123",
                "full_name": "User Four",
                "role": "user",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": 6,
                "email": "user5@company.com",
                "password": "user123",
                "full_name": "User Five",
                "role": "user",
                "created_at": "2024-01-01T00:00:00"
            }
        ]
    
    def generate_default_attendance(self) -> List[Dict]:
        """Generate default attendance data"""
        attendance_records = []
        record_id = 1
        
        # Start from April 1, 2025
        start_date = datetime(2025, 4, 1)
        # End at July 2, 2025
        end_date = datetime(2025, 7, 2)
        
        default_users = self.get_default_users()
        for user in default_users[1:]:  # Skip admin user
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
    
    # User operations
    def get_users(self) -> List[Dict]:
        """Get all users"""
        return self.data['users']
    
    def add_user(self, user_data: Dict) -> Dict:
        """Add a new user with auto-generated ID"""
        # Auto-generate user ID
        max_id = max([u["id"] for u in self.data['users']], default=0)
        user_data['id'] = max_id + 1
        user_data['created_at'] = datetime.now().isoformat()
        self.data['users'].append(user_data)
        self.save_data()
        return user_data
    
    def delete_user(self, user_id: int) -> Dict:
        """Delete a user and store for undo"""
        user_to_delete = next((u for u in self.data['users'] if u["id"] == user_id), None)
        if not user_to_delete:
            return None
            
        # Store user data for undo functionality
        user_attendance = [r for r in self.data['attendance'] if r["user_id"] == user_id]
        user_todos = [t for t in self.data['todos'] if t["user_id"] == user_id]
        
        deleted_user_data = {
            "user": user_to_delete,
            "attendance": user_attendance,
            "todos": user_todos,
            "deleted_at": datetime.now().isoformat()
        }
        self.data['deleted_users'].append(deleted_user_data)
        
        # Remove user from users
        self.data['users'] = [u for u in self.data['users'] if u["id"] != user_id]
        
        # Remove all attendance records
        self.data['attendance'] = [r for r in self.data['attendance'] if r["user_id"] != user_id]
        
        # Remove all todos
        self.data['todos'] = [t for t in self.data['todos'] if t["user_id"] != user_id]
        
        self.save_data()
        return deleted_user_data
    
    def undo_user_deletion(self, user_id: int) -> Dict:
        """Restore a deleted user"""
        deleted_user_data = next((d for d in self.data['deleted_users'] if d["user"]["id"] == user_id), None)
        if not deleted_user_data:
            return None
            
        # Restore user
        self.data['users'].append(deleted_user_data["user"])
        
        # Restore attendance records
        self.data['attendance'].extend(deleted_user_data["attendance"])
        
        # Restore todos
        self.data['todos'].extend(deleted_user_data["todos"])
        
        # Remove from deleted users list
        self.data['deleted_users'] = [d for d in self.data['deleted_users'] if d["user"]["id"] != user_id]
        
        self.save_data()
        return deleted_user_data
    
    # Attendance operations
    def get_attendance(self, user_id: int = None, month: int = None, year: int = None) -> List[Dict]:
        """Get attendance records with optional filters"""
        records = self.data['attendance']
        
        if user_id:
            records = [r for r in records if r.get("user_id") == user_id]
            
        if month is not None or year is not None:
            filtered_records = []
            for record in records:
                try:
                    record_date = datetime.strptime(record["date"], "%Y-%m-%d")
                    if year is not None and record_date.year != year:
                        continue
                    if month is not None and record_date.month != month:
                        continue
                    filtered_records.append(record)
                except:
                    continue
            records = filtered_records
            
        return records
    
    def add_attendance(self, attendance_data: Dict) -> Dict:
        """Add attendance record"""
        # Check if attendance already exists for this user and date
        existing_record = next(
            (r for r in self.data['attendance'] 
             if r["user_id"] == attendance_data["user_id"] and r["date"] == attendance_data["date"]),
            None
        )
        
        if existing_record:
            # Update existing record
            existing_record["status"] = attendance_data["status"]
            existing_record["notes"] = attendance_data.get("notes")
            self.save_data()
            return existing_record
        
        # Create new record
        new_record = {
            "id": len(self.data['attendance']) + 1,
            **attendance_data
        }
        self.data['attendance'].append(new_record)
        self.save_data()
        return new_record
    
    def delete_attendance(self, attendance_id: int) -> Dict:
        """Delete attendance record"""
        for i, record in enumerate(self.data['attendance']):
            if record["id"] == attendance_id:
                deleted_record = self.data['attendance'].pop(i)
                self.save_data()
                return deleted_record
        return None
    
    # Todo operations
    def get_todos(self, user_id: int = None) -> List[Dict]:
        """Get todos with optional user filter"""
        if user_id:
            return [todo for todo in self.data['todos'] if todo.get("user_id") == user_id]
        return self.data['todos']
    
    def add_todo(self, todo_data: Dict) -> Dict:
        """Add a new todo"""
        new_todo = {
            "id": len(self.data['todos']) + 1,
            **todo_data
        }
        if 'date_created' not in new_todo:
            new_todo['date_created'] = datetime.now().strftime("%Y-%m-%d")
        
        self.data['todos'].append(new_todo)
        self.save_data()
        return new_todo
    
    def update_todo(self, todo_id: int, notes: str) -> Dict:
        """Update a todo"""
        for i, todo in enumerate(self.data['todos']):
            if todo["id"] == todo_id:
                self.data['todos'][i]["notes"] = notes
                self.save_data()
                return self.data['todos'][i]
        return None
    
    def delete_todo(self, todo_id: int) -> Dict:
        """Delete a todo"""
        for i, todo in enumerate(self.data['todos']):
            if todo["id"] == todo_id:
                deleted_todo = self.data['todos'].pop(i)
                self.save_data()
                return deleted_todo
        return None

# Global database instance
db = SimpleDatabase()
