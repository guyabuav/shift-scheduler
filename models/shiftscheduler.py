import json
from datetime import datetime, timedelta
from models.shift import Shift


class ShiftScheduler:
    def __init__(self, employees):
        self.employees = employees
        self.shifts = []
        self.workload_matrix = {
            emp: [[0 for _ in range(3)] for _ in range(7)] for emp in employees
        }

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

    def assign_shifts(self, week_start_date):

        employee_daily_shifts = {emp: set() for emp in self.employees}
        assigned_shifts = {emp: 0 for emp in self.employees}
        shift_types_assigned = {emp: set() for emp in self.employees}

        week_shifts = [s for s in self.shifts if self.is_in_week(s.date, week_start_date)]

        # Step 1 - Fill each shift with 1 employee at least
        print("\n🔄 Step 1: Assigning at least one employee per shift")

        for shift in week_shifts:
            day_index = (datetime.strptime(shift.date, "%d/%m/%Y").weekday() + 1) % 7
            shift_index = ["Morning", "Evening", "Night"].index(shift.shift_type)
            best_employee = self.find_best_employee(shift, assigned_shifts, shift_types_assigned, employee_daily_shifts,
                                                    week_start_date)
            if best_employee:
                shift.add_employee(best_employee)
                assigned_shifts[best_employee] += 1
                shift_types_assigned[best_employee].add(shift.shift_type)
                employee_daily_shifts[best_employee].add(shift.date)
                self.workload_matrix[best_employee][day_index][shift_index] += 1
                print(f"✅ {best_employee.full_name} assigned to {shift.shift_type} on {shift.date}")

        # Step 2 - Fill for each employee for 5 shifts
        print("\n🔄 Step 2: Assigning additional shifts so every employee has 5 shifts")
        for shift in week_shifts:
            while len(shift.employees) < shift.max_employees:
                best_employee = self.find_best_employee(shift, assigned_shifts, shift_types_assigned,
                                                        employee_daily_shifts, week_start_date, allow_doubles=True)
                if not best_employee or assigned_shifts[best_employee] >= 5:
                    break
                day_index = (datetime.strptime(shift.date, "%d/%m/%Y").weekday() + 1) % 7
                shift_index = ["Morning", "Evening", "Night"].index(shift.shift_type)
                shift.add_employee(best_employee)
                assigned_shifts[best_employee] += 1
                shift_types_assigned[best_employee].add(shift.shift_type)
                employee_daily_shifts[best_employee].add(shift.date)
                self.workload_matrix[best_employee][day_index][shift_index] += 1
                print(f"✅ {best_employee.full_name} assigned to additional shift {shift.shift_type} on {shift.date}")

    def find_best_employee(self, shift, assigned_shifts, shift_types_assigned, employee_daily_shifts,
                           week_start_date, allow_doubles=False):
        available_employees = [emp for emp in self.employees if not self.has_constraint(emp, shift, week_start_date)]

        if not available_employees:
            return None

        day_index = (datetime.strptime(shift.date, "%d/%m/%Y").weekday() + 1) % 7
        shift_index = ["Morning", "Evening", "Night"].index(shift.shift_type)

        available_employees.sort(key=lambda emp: (
            assigned_shifts[emp],
            self.workload_matrix[emp][day_index][shift_index],
            0 if shift.shift_type not in shift_types_assigned[emp] else 1
        ))

        for employee in available_employees:
            if not allow_doubles and assigned_shifts[employee] >= 5:
                continue
            if self.has_insufficient_rest(employee, shift):
                continue
            if shift.date in employee_daily_shifts[employee]:
                continue
            return employee

        return None

    def has_constraint(self, employee, shift, week_start_date):
        shift_date = datetime.strptime(shift.date, "%d/%m/%Y")
        week_start = datetime.strptime(week_start_date, "%d/%m/%Y")

        week_key = week_start.strftime("%d/%m/%Y")

        print(f"🔍 Checking constraint for {employee.full_name} on {shift.date} - {shift.shift_type}")
        print(f"    Week constraints in JSON: {json.dumps(employee.constraints, indent=4)}")

        day_name = shift_date.strftime("%A")

        week_constraints = employee.constraints.get(week_key, {})

        if not week_constraints:
            print(f"⚠️ No constraints found for week {week_key} - Assuming no constraints.")
            return False

        day_constraints = week_constraints.get(day_name, [])

        has_restriction = shift.shift_type in day_constraints

        print(f"    Found constraint: {has_restriction}")

        return has_restriction

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

    def print_employee_shifts(self, employee, week_start_date):
        week_shifts = [shift for shift in self.shifts if
                       employee in shift.employees and self.is_in_week(shift.date, week_start_date)]

        if not week_shifts:
            print(f"❌ {employee.full_name} has no assigned shifts for the week starting {week_start_date}.")
            return

        print(f"\n📅 Shifts for {employee.full_name} in the week starting {week_start_date}:")
        for shift in week_shifts:
            print(f"   🕒 {shift.date} - {shift.shift_type}")

    def print_workload_matrix(self):
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        shifts = ["Morning", "Evening", "Night"]

        print("\n📊 Workload Matrix:")
        for emp in self.employees:
            print(f"\n👤 {emp.full_name}:")
            print("-" * 50)
            print(f"{'Day':<10}{'Morning':<10}{'Evening':<10}{'Night':<10}")
            print("-" * 50)

            for day_idx, day in enumerate(days):
                row = f"{day:<10}"
                for shift_idx in range(3):
                    row += f"{self.workload_matrix[emp][day_idx][shift_idx]:<10}"
                print(row)

            print("-" * 50)

    def is_in_week(self, shift_date, week_start_date):
        shift_date = datetime.strptime(shift_date, "%d/%m/%Y")
        week_start = datetime.strptime(week_start_date, "%d/%m/%Y")
        week_end = week_start + timedelta(days=6)
        return week_start <= shift_date <= week_end

    def get_employee_shifts(self, username, week_start_date):
        employee_shifts = []
        for shift in self.shifts:
            if self.is_in_week(shift.date, week_start_date):
                for emp in shift.employees:
                    if emp.user_id == username:
                        employee_shifts.append(shift)
        return employee_shifts
