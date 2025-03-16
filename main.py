import tkinter as tk
from models.employee import Employee
from models.manager import Manager
from models.login import LoginManager
from models.login_gui import LoginGUI
from models.shiftscheduler import ShiftScheduler
from models.shiftscheduler_gui import ShiftSchedulerGUI
from models.employeeschedule_gui import EmployeeScheduleGUI

emp1 = Employee("guy abuav", 1996, 8784778, "guyabuav@gmail.com", 39371, "guyabuav", "#####", None)
emp2 = Employee("matan rak", 1992, 874312378, "rakoon@gmail.com", 39372, "matanrak", "#####", None)
emp3 = Employee("bibi net", 1292, 8743131321, "bibon@gmail.com", 39373, "bibinet", "#####", None)
emp4 = Employee("amit ron", 2312, 25123123, "amiton@gmail.com", 39374, "amitron", "#####", None)
emp5 = Employee("dankof", 12332, 123131321, "danon@gmail.com", 39375, "dankof", "#####", None)
emp6 = Employee("chen os", 1222, 80131321, "chenos@gmail.com", 39376, "chinos", "#####", None)
manager1 = Manager("bibi bo", 1292, 8743131321, "bibon@gmail.com", 39373, "admin", "#####", None)
employee_list = [emp1, emp2, emp3, emp4, emp5, emp6]

shift_scheduler = ShiftScheduler(employee_list)
shift_scheduler.create_weekly_shifts("02/03/2025")
shift_scheduler.create_weekly_shifts("09/03/2025")
shift_scheduler.create_weekly_shifts("16/03/2025")
shift_scheduler.create_weekly_shifts("23/03/2025")
shift_scheduler.create_weekly_shifts("30/03/2025")
shift_scheduler.create_weekly_shifts("06/04/2025")
shift_scheduler.create_weekly_shifts("13/04/2025")
shift_scheduler.create_weekly_shifts("20/04/2025")
shift_scheduler.create_weekly_shifts("27/04/2025")

login_manager = LoginManager()


def open_login_gui():
    root = tk.Tk()
    login_app = LoginGUI(root, on_login_success)
    root.mainloop()


def logout():
    try:
        root.quit()
        root.destroy()
    except tk.TclError:
        pass

    open_login_gui()


def on_login_success(username, role):
    root = tk.Tk()

    if role == "Manager":
        root.title(f"Manager Panel - {username}")
        app = ShiftSchedulerGUI(root, shift_scheduler, username, logout)
    else:
        root.title(f"Employee Panel - {username}")
        EmployeeScheduleGUI(root, shift_scheduler, username, logout)

    root.mainloop()


root = tk.Tk()
login_app = LoginGUI(root, on_login_success)
root.mainloop()
