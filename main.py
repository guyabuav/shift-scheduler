import tkinter as tk
from models.employee import Employee
from models.manager import Manager
from models.login import LoginManager
from models.login_gui import LoginGUI
from models.shiftscheduler import ShiftScheduler
from models.shiftscheduler_gui import ShiftSchedulerGUI
from models.employeeschedule_gui import EmployeeScheduleGUI

# יצירת עובדים ומנהל
emp1 = Employee("Guy Abuav", 1996, 8784778, "guyabuav@gmail.com", 39371, "guyabuav", "#####", None)
emp2 = Employee("Matan Rak", 1992, 874312378, "rakoon@gmail.com", 39372, "matanrak", "#####", None)
emp3 = Employee("Bibi Net", 1292, 8743131321, "bibon@gmail.com", 39373, "bibinet", "#####", None)
emp4 = Employee("amit ron", 2312, 25123123, "amiton@gmail.com", 39374, "amitron", "#####", None)
emp5 = Employee("dankof", 12332, 123131321, "danon@gmail.com", 39375, "dankof", "#####", None)
emp6 = Employee("chen os", 1222, 80131321, "chenos@gmail.com", 39376, "chinos", "#####", None)
manager1 = Manager("Bibi Net", 1292, 8743131321, "bibon@gmail.com", 39373, "admin", "#####", None)
employee_list = [emp1, emp2, emp3, emp4, emp5, emp6]

emp1.add_constraint("2/3/2025", "Sunday", "Morning")
emp1.add_constraint("2/3/2025", "Monday", "Morning")
emp1.add_constraint("2/3/2025", "Monday", "Morning")
emp1.add_constraint("2/3/2025", "Tuesday", "Morning")
emp1.add_constraint("2/3/2025", "Wednesday", "Morning")
emp1.add_constraint("2/3/2025", "Thursday", "Morning")

shift_scheduler = ShiftScheduler(employee_list)
shift_scheduler.create_weekly_shifts("2/3/2025")
shift_scheduler.create_weekly_shifts("9/3/2025")
shift_scheduler.create_weekly_shifts("16/3/2025")
shift_scheduler.create_weekly_shifts("23/3/2025")
shift_scheduler.create_weekly_shifts("30/3/2025")

print(emp1.constraints)  # 📌 בדוק שהנתונים נשמרו בזיכרון
emp1.save_constraints_to_file()  # 📌 שמור לקובץ





# shift_scheduler.print_employee_shifts(emp1, "2/3/2025")
# shift_scheduler.assign_shifts("2/3/2025")
# מערכת התחברות
login_manager = LoginManager()


# יצירת מחלקת שיבוץ

def open_login_gui():
    """ פותח מחדש את מסך ההתחברות """
    root = tk.Tk()
    login_app = LoginGUI(root, on_login_success)
    root.mainloop()

def logout():
    """ סוגר את ה-GUI ומחזיר למסך ההתחברות """
    try:
        root.quit()  # מסיים את ה-loop הראשי של tkinter
        root.destroy()  # סוגר את החלון הנוכחי אם הוא קיים
    except tk.TclError:
        pass  # אם החלון כבר סגור, אל תעשה כלום

    open_login_gui()  # פותח מחדש את מסך ההתחברות



def on_login_success(username, role):
    """ מופעל לאחר שהמשתמש מתחבר בהצלחה """
    root = tk.Tk()

    if role == "Manager":
        root.title(f"Manager Panel - {username}")
        app = ShiftSchedulerGUI(root, shift_scheduler, logout)
    else:
        root.title(f"Employee Panel - {username}")
        EmployeeScheduleGUI(root, shift_scheduler, username, logout)

    root.mainloop()


# הפעלת מסך התחברות במקום להפעיל את ה-GUI מיד
root = tk.Tk()
login_app = LoginGUI(root, on_login_success)
root.mainloop()

def open_login_gui():
    """ פותח מחדש את מסך ההתחברות """
    root = tk.Tk()
    login_app = LoginGUI(root, on_login_success)
    root.mainloop()
