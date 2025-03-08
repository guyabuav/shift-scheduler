from datetime import datetime, timedelta
from models.shift import Shift


class ShiftScheduler:
    def __init__(self, employees):
        self.employees = employees
        self.shifts = []
        self.workload_matrix = {emp: {} for emp in employees}

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
        employee_shift_types = {emp: set() for emp in self.employees}
        assigned_shifts = {emp: 0 for emp in self.employees}
        employee_daily_shifts = {emp: set() for emp in self.employees}

        max_failed_attempts = 10  # מספר ניסיונות כושלים מקסימלי לפני ויתור

        ### 🟢 **שלב 1: כל עובד יקבל לפחות 5 משמרות**
        print("\n🔄 Step 1: Ensuring every employee gets 5 shifts")

        failed_attempts = {emp: 0 for emp in self.employees}  # מעקב אחרי ניסיונות כושלים

        for employee in self.employees:
            while assigned_shifts[employee] < 5:
                shift_assigned = False  # מעקב אם העובד שובץ בהצלחה
                for shift in self.shifts:
                    shift_date = datetime.strptime(shift.date, "%d/%m/%Y")
                    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                    day_name = days[(shift_date.weekday() + 1) % 7]
                    shift_key = f"{day_name}-{shift.shift_type}"

                    if len(shift.employees) >= shift.max_employees:
                        continue

                    if employee in shift.employees:
                        continue

                    if self.has_insufficient_rest(employee, shift_date, shift.shift_type):
                        failed_attempts[employee] += 1
                        if failed_attempts[employee] > max_failed_attempts:
                            print(f"⚠️ Too many failed attempts for {employee.full_name}, skipping permanently!")
                            break
                        continue

                    if shift_date.strftime("%d/%m/%Y") in employee_daily_shifts[employee]:
                        continue

                    shift.add_employee(employee)
                    assigned_shifts[employee] += 1
                    self.workload_matrix[employee][shift_key] = \
                        self.workload_matrix[employee].get(shift_key, 0) + 1
                    employee_shift_types[employee].add(shift.shift_type)
                    employee_daily_shifts[employee].add(shift_date.strftime("%d/%m/%Y"))

                    print(f"✅ {employee.full_name} assigned to {shift_key} on {shift.date}")

                    shift_assigned = True
                    break  # יציאה מהלולאה כדי לעבור למשמרת הבאה

                if not shift_assigned:  # אם העובד לא שובץ בשום משמרת, נפסיק לנסות אותו
                    print(f"⚠️ No available shifts for {employee.full_name}, stopping assignment.")
                    break

    def has_insufficient_rest(self, employee, shift_date, shift_type):
        """בודק אם לעובד יש מספיק מנוחה בין המשמרות."""

        prev_shift_type = {"Morning": "Night", "Evening": "Morning", "Night": "Evening"}

        if shift_type not in prev_shift_type:
            return False  # אם המשמרת היא לא בוקר, ערב או לילה, אין מגבלת מנוחה

        prev_date = shift_date - timedelta(days=1) if shift_type == "Morning" else shift_date
        prev_shift = prev_shift_type.get(shift_type, None)  # נוודא שזה לא מחזיר None

        if not prev_shift:
            return False  # אם אין משמרת קודמת, אין צורך לבדוק מנוחה

        prev_shift_key = f"{prev_date.strftime('%A')}-{prev_shift}"

        for shift in self.shifts:
            if shift.date == prev_date.strftime("%d/%m/%Y") and shift.shift_type == prev_shift:
                if employee in shift.employees:
                    print(f"⚠️ {employee.full_name} worked {prev_shift} on {prev_date.strftime('%d/%m/%Y')}, skipping")
                    return True  # העובד עבד במשמרת הקודמת ולכן אין לו מספיק מנוחה

        return False  # יש מספיק מנוחה

    def available_employees(self, shift_key):
        return [emp for emp in self.employees if shift_key.split("-")[1] not in emp.constraints.get(shift_key.split("-")[0], [])]

    def find_minimum_weight(self, shift_key, employee_shift_types, shift_date, tried_employees):
        available_emp = self.available_employees(shift_key)
        best_employee = None
        lowest_weight = float('inf')

        for employee in available_emp:
            if employee in tried_employees:
                continue

            weight = self.workload_matrix.get(employee, {}).get(shift_key, 0)

            if shift_key.split("-")[1] not in employee_shift_types[employee]:
                weight -= 1

            if weight < lowest_weight:
                lowest_weight = weight
                best_employee = employee

        return best_employee

    def get_employee_shift_count(self, employee):
        return sum(1 for shift in self.shifts if employee in shift.employees)
