import json
import os
from datetime import datetime, timedelta
from tkinter import messagebox

from models.shift import Shift


class ShiftScheduler:
    def __init__(self, employees):
        self.employees = employees
        self.shifts = []
        self.workload_matrix = {
            emp: [[0 for _ in range(3)] for _ in range(7)] for emp in employees
        }
        self.assigned_shifts = {emp: 0 for emp in self.employees}
        self.load_workload_matrix()
        self.load_schedule_from_file()

    def create_weekly_shifts(self, start_date):
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        shift_types = ["Morning", "Evening", "Night"]
        base_date = datetime.strptime(start_date, "%d/%m/%Y")

        existing_shifts = [s for s in self.shifts if self.is_in_week(s.date, start_date)]
        if existing_shifts:
            return

        for i, day in enumerate(days):
            for shift_type in shift_types:
                shift_date = base_date + timedelta(days=i)
                max_employees = 1 if shift_type == "Night" or (day == "Friday" and shift_type == "Evening") else 2
                self.shifts.append(Shift(shift_date.strftime("%d/%m/%Y"), shift_type, max_employees=max_employees))

        self.save_schedule_to_file()

    def assign_shifts(self, week_start_date):

        existing_shifts = [s for s in self.shifts if self.is_in_week(s.date, week_start_date) and s.employees]

        if existing_shifts:
            messagebox.showerror(f"Error❌ Schedule for {week_start_date} Already exists")
            return

        employee_daily_shifts = {emp: set() for emp in self.employees}
        assigned_shifts = {emp: 0 for emp in self.employees}
        shift_types_assigned = {emp: set() for emp in self.employees}

        week_shifts = [s for s in self.shifts if self.is_in_week(s.date, week_start_date)]

        print("\n🔄 Assigning shifts - Ensuring all shifts are covered")

        all_shifts_filled = False
        while not all_shifts_filled:
            all_shifts_filled = True

            for shift in week_shifts:
                if len(shift.employees) == 0:
                    best_employee = self.find_best_employee(shift, assigned_shifts, shift_types_assigned,
                                                            employee_daily_shifts, week_start_date)
                    if best_employee:
                        shift.add_employee(best_employee)
                        assigned_shifts[best_employee] += 1
                        shift_types_assigned[best_employee].add(shift.shift_type)
                        employee_daily_shifts[best_employee].add(shift.date)

                        day_index = (datetime.strptime(shift.date, "%d/%m/%Y").weekday() + 1) % 7
                        shift_index = ["Morning", "Evening", "Night"].index(shift.shift_type)
                        self.workload_matrix[best_employee][day_index][shift_index] += 1

                        print(f"✅ {best_employee.full_name} assigned to {shift.shift_type} on {shift.date}")
                    else:
                        all_shifts_filled = False

        print("\n🔄 Assigning shifts - Ensuring each employee has 5 shifts")

        all_employees_filled = False
        while not all_employees_filled:
            all_employees_filled = True

            for employee in self.employees:
                if assigned_shifts[employee] < 5:
                    for shift in week_shifts:
                        if len(shift.employees) < shift.max_employees:
                            best_employee = self.find_best_employee(shift, assigned_shifts, shift_types_assigned,
                                                                    employee_daily_shifts, week_start_date,
                                                                    allow_doubles=True)
                            if best_employee and best_employee == employee:
                                shift.add_employee(best_employee)
                                assigned_shifts[best_employee] += 1
                                shift_types_assigned[best_employee].add(shift.shift_type)
                                employee_daily_shifts[best_employee].add(shift.date)

                                day_index = (datetime.strptime(shift.date, "%d/%m/%Y").weekday() + 1) % 7
                                shift_index = ["Morning", "Evening", "Night"].index(shift.shift_type)
                                self.workload_matrix[best_employee][day_index][shift_index] += 1

                                break

                    if assigned_shifts[employee] < 5:
                        all_employees_filled = False

        self.save_schedule_to_file()
        self.save_workload_matrix()

    def find_best_employee(self, shift, assigned_shifts, shift_types_assigned, employee_daily_shifts,
                           week_start_date, allow_doubles=False):
        available_employees = [emp for emp in self.employees if not self.has_constraint(emp, shift, week_start_date)]

        if not available_employees:
            return None

        day_index = (datetime.strptime(shift.date, "%d/%m/%Y").weekday() + 1) % 7
        shift_index = ["Morning", "Evening", "Night"].index(shift.shift_type)

        available_employees.sort(key=lambda emp: (
            self.workload_matrix[emp][day_index][shift_index],
            0 if shift.shift_type not in shift_types_assigned[emp] else 1,
            assigned_shifts[emp]
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

        day_name = shift_date.strftime("%A")
        week_constraints = employee.constraints.get(week_key, {})

        return shift.shift_type in week_constraints.get(day_name, [])

    def has_insufficient_rest(self, employee, shift):
        shift_date = datetime.strptime(shift.date, "%d/%m/%Y")
        prev_date = shift_date - timedelta(days=1)

        previous_shifts = [s for s in self.shifts if
                           s.date == prev_date.strftime("%d/%m/%Y") and employee in s.employees]

        return any(s.shift_type == "Night" and shift.shift_type == "Morning" for s in previous_shifts)

    def is_in_week(self, shift_date, week_start_date):
        shift_date = datetime.strptime(shift_date, "%d/%m/%Y")
        week_start = datetime.strptime(week_start_date, "%d/%m/%Y")
        week_end = week_start + timedelta(days=6)
        return week_start <= shift_date <= week_end

    def get_employee_shifts(self, username, week_start_date):
        return [shift for shift in self.shifts if
                self.is_in_week(shift.date, week_start_date) and any(
                    emp.user_id == username for emp in shift.employees)]

    def save_schedule_to_file(self):
        file_path = "schedule.json"
        try:
            schedule_data = [
                {
                    "date": shift.date,
                    "shift_type": shift.shift_type,
                    "max_employees": shift.max_employees,
                    "employees": [emp.user_id for emp in shift.employees]
                }
                for shift in self.shifts
            ]

            with open(file_path, "w") as file:
                json.dump(schedule_data, file, indent=4)

            print("✅ Schedule saved successfully!")

        except Exception as e:
            print(f"❌ Error saving schedule: {e}")

    def load_schedule_from_file(self):
        file_path = "schedule.json"
        if not os.path.exists(file_path):
            print("⚠️ schedule.json not found. Starting with an empty schedule.")
            return

        try:
            with open(file_path, "r") as file:
                data = file.read().strip()
                if not data:
                    print("⚠️ schedule.json is empty!")
                    return

                schedule_data = json.loads(data)
                self.shifts = []

                for shift_info in schedule_data:
                    shift = Shift(shift_info["date"], shift_info["shift_type"], shift_info["max_employees"])
                    for user_id in shift_info["employees"]:
                        emp = next((e for e in self.employees if e.user_id == user_id), None)
                        if emp:
                            shift.add_employee(emp)

                    self.shifts.append(shift)

                print("✅ Schedule loaded successfully!")

        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON format in schedule.json: {e}")
        except Exception as e:
            print(f"⚠️ Error loading schedule: {e}")

    def save_workload_matrix(self):
        file_path = "workload_matrix.json"
        try:
            matrix_data = {
                emp.user_id: self.workload_matrix[emp] for emp in self.employees
            }
            print(f"Saving workload matrix: {matrix_data}")
            with open(file_path, "w") as file:
                json.dump(matrix_data, file, indent=4)
            print("✅ Workload matrix saved successfully!")
        except Exception as e:
            print(f"❌ Error saving workload matrix: {e}")

    def load_workload_matrix(self):
        file_path = "workload_matrix.json"
        if not os.path.exists(file_path):
            print("⚠️ Workload matrix file not found. Starting fresh.")
            return

        try:
            with open(file_path, "r") as file:
                data = file.read().strip()
                if not data:
                    return

                matrix_data = json.loads(data)
                print(f"🔍 Loaded workload matrix: {matrix_data}")

                for emp in self.employees:
                    if emp.user_id in matrix_data:
                        self.workload_matrix[emp] = matrix_data[emp.user_id]

                print("✅ Workload matrix loaded successfully!")

        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON format in workload_matrix.json: {e}")
        except Exception as e:
            print(f"⚠️ Error loading workload matrix: {e}")
