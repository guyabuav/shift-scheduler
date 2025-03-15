from datetime import datetime


class Shift:
    def __init__(self, date, shift_type, max_employees):
        self.date = date
        self.shift_type = shift_type
        self.max_employees = max_employees
        self.employees = []

    def add_employee(self, employee):
        if employee in self.employees:
            print(f"This employee already working on this shift")
        if len(self.employees) < self.max_employees:
            self.employees.append(employee)
            print(f"{employee} was added to {self}")
        else:
            print("The maximum employees for this shift already reached")

    def remove_employee(self, employee):
        self.employees.remove(employee)
        print(f"{employee} was removed from {self}")

    def __str__(self):
        date_obj = datetime.strptime(self.date, "%d/%m/%Y")
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        day_name = days[(date_obj.weekday() + 1) % 7]
        employee_names = [emp.full_name for emp in self.employees]
        return f"Shift: {self.date}, {day_name}, Shift_type: {self.shift_type}, " \
               f"Max_employees: {self.max_employees}, Employees: {employee_names}"

    def print_shift_employee(self):
        for i, employee in enumerate(self.employees):
            print(f"{i+1}. {employee}")
