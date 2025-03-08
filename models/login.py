from models.manager import Manager


class Login():
    def __init__(self, users):
        self.users = users

    def authenticate(self, username, password):
        for user in self.users:
            if user.user_id == username and user.password == password:
                print(f"Welcome {user.full_name}, ({'Manager' if isinstance(user,Manager) else 'Employee'})")
                return user
        print("Invalid credentials. please try again")
        return None

    def access_scheduler(user, scheduler):
        """Allow only managers to manage ShiftScheduler."""
        if isinstance(user, Manager):
            print("✅ Access granted to ShiftScheduler.")
            return scheduler
        else:
            print("❌ Access denied. Only managers can modify shifts.")
            return None
