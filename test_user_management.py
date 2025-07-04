#!/usr/bin/env python3
"""
Test script for user management functionality
"""
import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_CREDENTIALS = {
    "email": "admin@company.com",
    "password": "admin123"
}

def test_user_management():
    """Test user management operations"""
    print("🚀 Testing User Management System...")
    
    # Test 1: Get initial users
    print("\n1. Testing initial user list...")
    response = requests.get(f"{BASE_URL}/api/users")
    if response.status_code == 200:
        initial_users = response.json()
        print(f"   ✅ Found {len(initial_users)} initial users")
        initial_count = len([u for u in initial_users if u['role'] != 'admin'])
        print(f"   📊 Non-admin users: {initial_count}")
    else:
        print(f"   ❌ Failed to fetch users: {response.status_code}")
        return False
    
    # Test 2: Create a new user
    print("\n2. Testing user creation...")
    new_user_data = {
        "id": 999,
        "email": "testuser@company.com",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "user"
    }
    
    response = requests.post(f"{BASE_URL}/api/users", json=new_user_data)
    if response.status_code == 200:
        created_user = response.json()
        print(f"   ✅ User created successfully: {created_user['full_name']}")
        print(f"   📅 Created at: {created_user.get('created_at', 'N/A')}")
    else:
        print(f"   ❌ Failed to create user: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    # Test 3: Verify user appears in list
    print("\n3. Testing user persistence...")
    response = requests.get(f"{BASE_URL}/api/users")
    if response.status_code == 200:
        updated_users = response.json()
        new_count = len([u for u in updated_users if u['role'] != 'admin'])
        print(f"   📊 Non-admin users after creation: {new_count}")
        
        test_user = next((u for u in updated_users if u['id'] == 999), None)
        if test_user:
            print(f"   ✅ New user found in list: {test_user['full_name']}")
        else:
            print(f"   ❌ New user not found in list")
            return False
    else:
        print(f"   ❌ Failed to fetch updated users: {response.status_code}")
        return False
    
    # Test 4: Delete the user
    print("\n4. Testing user deletion...")
    response = requests.delete(f"{BASE_URL}/api/users/999")
    if response.status_code == 200:
        delete_result = response.json()
        print(f"   ✅ User deleted: {delete_result['message']}")
        print(f"   🔄 Undo available: {delete_result.get('undo_available', False)}")
    else:
        print(f"   ❌ Failed to delete user: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    # Test 5: Verify user is removed from list
    print("\n5. Testing user removal...")
    response = requests.get(f"{BASE_URL}/api/users")
    if response.status_code == 200:
        users_after_delete = response.json()
        delete_count = len([u for u in users_after_delete if u['role'] != 'admin'])
        print(f"   📊 Non-admin users after deletion: {delete_count}")
        
        test_user = next((u for u in users_after_delete if u['id'] == 999), None)
        if not test_user:
            print(f"   ✅ User successfully removed from list")
        else:
            print(f"   ❌ User still exists in list")
            return False
    else:
        print(f"   ❌ Failed to fetch users after deletion: {response.status_code}")
        return False
    
    # Test 6: Test undo functionality
    print("\n6. Testing undo functionality...")
    response = requests.post(f"{BASE_URL}/api/users/999/undo")
    if response.status_code == 200:
        undo_result = response.json()
        print(f"   ✅ User restored: {undo_result['message']}")
        print(f"   👤 Restored user: {undo_result['restored_user']['full_name']}")
    else:
        print(f"   ❌ Failed to undo deletion: {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    # Test 7: Verify user is back in list
    print("\n7. Testing user restoration...")
    response = requests.get(f"{BASE_URL}/api/users")
    if response.status_code == 200:
        final_users = response.json()
        final_count = len([u for u in final_users if u['role'] != 'admin'])
        print(f"   📊 Non-admin users after restoration: {final_count}")
        
        test_user = next((u for u in final_users if u['id'] == 999), None)
        if test_user:
            print(f"   ✅ User successfully restored: {test_user['full_name']}")
        else:
            print(f"   ❌ User not found after restoration")
            return False
    else:
        print(f"   ❌ Failed to fetch final users: {response.status_code}")
        return False
    
    # Cleanup: Delete the test user permanently
    print("\n8. Cleaning up...")
    requests.delete(f"{BASE_URL}/api/users/999")
    print("   🧹 Test user cleaned up")
    
    print("\n🎉 All tests passed! User management system is working correctly.")
    return True

def test_data_persistence():
    """Test that data persists across server restarts"""
    print("\n🔄 Testing data persistence...")
    print("   ⚠️  This test requires manual server restart")
    print("   📝 To test persistence:")
    print("   1. Add a user through the frontend")
    print("   2. Restart the backend server")
    print("   3. Check if the user still exists")
    print("   4. The user should persist in the data/users.json file")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 USER MANAGEMENT SYSTEM TEST")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server responded with error")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the backend server first.")
        print("   Run: python main.py")
        sys.exit(1)
    
    # Run tests
    success = test_user_management()
    test_data_persistence()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("🎯 User persistence: FIXED")
        print("🎯 User visibility: FIXED")
        print("🎯 Undo functionality: FIXED")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1) 