from datetime import datetime, timedelta
from models.shift import Shift


class ShiftScheduler:
    def __init__(self, employees):
        self.employees = employees
        self.shifts = []
        self.workload_matrix = {emp: 0 for emp in employees}

    def create_weekly_shifts(self, start_date):
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        shift_types = ["Morning", "Evening", "Night"]
        base_date = datetime.strptime(start_date, "%d/%m/%Y")

        for i, day in enumerate(days):
            for shift_type in shift_types:
                shift_date = base_date + timedelta(days=i)
                max_employees = 1 if shift_type == "Night" or (day == "Friday" and shift_type == "Evening") else 2
                self.shifts.append(Shift(shift_date.strftime("%d/%m/%Y"), shift_type, max_employees=max_employees))

    def print_schedule(self):
        if not self.shifts:
            print("There is no scheduled shifts in this week")
        else:
            for shift in self.shifts:
                print(f"{shift}")

    def assign_shifts(self):
        employee_daily_shifts = {emp: set() for emp in self.employees}
        assigned_shifts = {emp: 0 for emp in self.employees}
        shift_types_assigned = {emp: set() for emp in self.employees}

        # Step 1 - Fill each shift with 1 employee at least
        print("\n🔄 Step 1: Assigning at least one employee per shift")
        for shift in self.shifts:
            best_employee = self.find_best_employee(shift, assigned_shifts, shift_types_assigned, employee_daily_shifts)
            if best_employee:
                shift.add_employee(best_employee)
                assigned_shifts[best_employee] += 1
                shift_types_assigned[best_employee].add(shift.shift_type)
                employee_daily_shifts[best_employee].add(shift.date)
                self.workload_matrix[best_employee] += 1
                print(f"✅ {best_employee.full_name} assigned to {shift.shift_type} on {shift.date}")

        # Step 2 - Fill for each employee for 5 shifts
        print("\n🔄 Step 2: Assigning additional shifts so every employee has 5 shifts")
        for shift in self.shifts:
            while len(shift.employees) < shift.max_employees:
                best_employee = self.find_best_employee(shift, assigned_shifts, shift_types_assigned,
                                                        employee_daily_shifts, allow_doubles=True)
                if not best_employee or assigned_shifts[best_employee] >= 5:
                    break

                shift.add_employee(best_employee)
                assigned_shifts[best_employee] += 1
                shift_types_assigned[best_employee].add(shift.shift_type)
                employee_daily_shifts[best_employee].add(shift.date)
                self.workload_matrix[best_employee] += 1
                print(f"✅ {best_employee.full_name} assigned to additional shift {shift.shift_type} on {shift.date}")

    def find_best_employee(self, shift, assigned_shifts, shift_types_assigned, employee_daily_shifts,
                           allow_doubles=False):
        available_employees = [emp for emp in self.employees if not self.has_constraint(emp, shift)]

        available_employees.sort(key=lambda emp: (
            assigned_shifts[emp],
            0 if shift.shift_type not in shift_types_assigned[emp] else 1))

        for employee in available_employees:
            if not allow_doubles and assigned_shifts[employee] >= 5:
                continue
            if self.has_insufficient_rest(employee, shift):
                continue
            if shift.date in employee_daily_shifts[employee]:
                continue
            return employee

        return None

    def has_constraint(self, employee, shift):  # Checking if employee have constraints for specific shift
        shift_date = datetime.strptime(shift.date, "%d/%m/%Y")
        day_name = shift_date.strftime("%A")
        return shift.shift_type in employee.constraints.get(day_name, [])

    def has_insufficient_rest(self, employee, shift):  # Checking 8 hours rest between 2 shifts
        shift_date = datetime.strptime(shift.date, "%d/%m/%Y")
        prev_date = shift_date - timedelta(days=1)

        previous_shifts = [s for s in self.shifts if
                           s.date == prev_date.strftime("%d/%m/%Y") and employee in s.employees]

        for s in previous_shifts:
            if s.shift_type == "Night" and shift.shift_type == "Morning":
                print(f"⚠️ {employee.full_name} worked Night before Morning on {shift.date}, skipping")
                return True

        return False

    def get_employee_shift_count(self, employee):  # Return amount of shift for each employee for week X
        return sum(1 for shift in self.shifts if employee in shift.employees)

    def print_employee_shifts(self, employee):
        employee_shifts = [shift for shift in self.shifts if employee in shift.employees]

        if not employee_shifts:
            print(f"❌ {employee.full_name} has no assigned shifts.")
            return

        print(f"\n📅 Shifts for {employee.full_name}:")
        for shift in employee_shifts:
            print(f"   🕒 {shift.date} - {shift.shift_type}")

    def print_workload_matrix(self):
        print("\n📊 Workload Matrix:")
        print("-" * 30)
        for emp in self.employees:
            print(f"👤 {emp.full_name}: {self.workload_matrix[emp]} shifts")
        print("-" * 30)

