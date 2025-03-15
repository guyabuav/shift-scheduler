from models.manager import Manager
import json
import os


class Login:
    def __init__(self, users):
        self.users = users

    def authenticate(self, username, password):
        for user in self.users:
            if user.user_id == username and user.password == password:
                print(f"Welcome {user.full_name}, ({'Manager' if isinstance(user, Manager) else 'Employee'})")
                return user
        print("Invalid credentials. please try again")
        return None

    def access_scheduler(self, user, scheduler):
        if isinstance(user, Manager):
            print("✅ Access granted to ShiftScheduler.")
            return scheduler
        else:
            print("❌ Access denied. Only managers can modify shifts.")
            return None


class LoginManager:
    USERS_FILE = "users.json"

    def __init__(self):
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.USERS_FILE):
            with open(self.USERS_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_users(self):
        with open(self.USERS_FILE, "w") as f:
            json.dump(self.users, f, indent=4)

    def register_user(self, username, password, role):
        if username in self.users:
            print("❌ User already exists!")
            return False
        self.users[username] = {"password": password, "role": role}
        self.save_users()
        print(f"✅ User {username} registered successfully!")
        return True

    def authenticate_user(self, username, password):
        user = self.users.get(username)
        if user and user["password"] == password:
            print(f"✅ {username} logged in as {user['role']}")
            return user["role"]
        print("❌ Invalid username or password!")
        return None
