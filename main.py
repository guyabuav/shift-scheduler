import tkinter as tk
from models.employee import Employee
from models.manager import Manager
from models.login import Login
from models.shiftscheduler import ShiftScheduler
from models.shiftscheduler_gui import ShiftSchedulerGUI

emp1 = Employee("Guy Abuav", 1996, 8784778, "guyabuav@gmail.com", 39371, "guyabuav", "pass", None)
emp2 = Employee("Matan Rak", 1992, 874312378, "rakoon@gmail.com", 39372, "matanrak", "pass", None)
emp3 = Employee("Bibi Net", 1292, 8743131321, "bibon@gmail.com", 39373, "bibinet", "pass", None)
emp4 = Employee("amit ron", 2312, 25123123, "amiton@gmail.com", 39374, "amitron", "pass", None)
emp5 = Employee("dankof", 12332, 123131321, "danon@gmail.com", 39375, "dankof", "pass", None)
emp6 = Employee("chen os", 1222, 80131321, "chenos@gmail.com", 39376, "chinos", "pass", None)
manager1 = Manager("Bibi Net", 1292, 8743131321, "bibon@gmail.com", 39373, "bibinet", "pass", None)
employee_list = [emp1, emp2, emp3, emp4, emp5, emp6]

login_system = Login(employee_list)
# username = input("Enter username: ")
# password = input("Enter password: ")
# user = login_system.authenticate(username, password)


emp1.add_constraint("Sunday", "Morning")
emp1.add_constraint("Sunday", "Evening")
emp1.add_constraint("Saturday", "Night")

emp2.add_constraint("Tuesday", "Morning")
emp2.add_constraint("Friday", "Night")
emp2.add_constraint("Wednesday", "Evening")

emp3.add_constraint("Monday", "Evening")
emp3.add_constraint("Thursday", "Morning")
emp3.add_constraint("Wednesday", "Night")

emp4.add_constraint("Wednesday", "Morning")
emp4.add_constraint("Sunday", "Evening")
emp4.add_constraint("Monday", "Night")

emp5.add_constraint("Tuesday", "Morning")
emp5.add_constraint("Friday", "Morning")
emp5.add_constraint("Friday", "Night")

shift_scheduler = ShiftScheduler(employee_list)
shift_scheduler.create_weekly_shifts("2/3/2025")
# shift_scheduler.assign_shifts("2/3/2025")

for employee in employee_list:
    print(f"{employee} assigned to {shift_scheduler.get_employee_shift_count(employee)}")

shift_scheduler.print_schedule()

shift_scheduler.print_employee_shifts(emp1, "2/3/2025")
shift_scheduler.print_employee_shifts(emp2, "2/3/2025")
shift_scheduler.print_employee_shifts(emp3, "2/3/2025")
shift_scheduler.print_employee_shifts(emp4, "2/3/2025")
shift_scheduler.print_employee_shifts(emp5, "2/3/2025")
shift_scheduler.print_employee_shifts(emp6, "2/3/2025")


shift_scheduler.print_workload_matrix()

shift_scheduler.create_weekly_shifts("9/3/2025")
# shift_scheduler.assign_shifts("9/3/2025")

for employee in employee_list:
    print(f"{employee} assigned to {shift_scheduler.get_employee_shift_count(employee)}")

shift_scheduler.print_schedule()

# הפעלת ה-GUI
root = tk.Tk()
app = ShiftSchedulerGUI(root, shift_scheduler)
root.mainloop()

# shift_scheduler.print_employee_shifts(emp1, "9/3/2025")
# shift_scheduler.print_employee_shifts(emp2, "9/3/2025")
# shift_scheduler.print_employee_shifts(emp3, "9/3/2025")
# shift_scheduler.print_employee_shifts(emp4, "9/3/2025")
# shift_scheduler.print_employee_shifts(emp5, "9/3/2025")
# shift_scheduler.print_employee_shifts(emp6, "9/3/2025")

# shift_scheduler.create_weekly_shifts("16/3/2025")
# shift_scheduler.assign_shifts("16/3/2025")

# shift_scheduler.create_weekly_shifts("23/3/2025")
# shift_scheduler.assign_shifts("23/3/2025")

# shift_scheduler.create_weekly_shifts("16/3/2025")
# shift_scheduler.assign_shifts("30/3/2025")

# shift_scheduler.create_weekly_shifts("6/4/2025")
# shift_scheduler.assign_shifts("6/4/2025")

# shift_scheduler.create_weekly_shifts("13/4/2025")
# shift_scheduler.assign_shifts("13/4/2025")

# shift_scheduler.create_weekly_shifts("20/4/2025")
# shift_scheduler.assign_shifts("20/4/2025")

# shift_scheduler.create_weekly_shifts("27/4/2025")
# shift_scheduler.assign_shifts("27/4/2025")

# shift_scheduler.print_workload_matrix()
