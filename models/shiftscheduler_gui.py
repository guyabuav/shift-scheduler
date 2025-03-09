import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from models.shiftscheduler import ShiftScheduler
from models.employee import Employee
from models.constraint_gui import ConstraintManager


class ShiftSchedulerGUI:
    def __init__(self, root, shift_scheduler, employee, logout_callback):
        self.root = root
        self.root.title("Shift Scheduler")

        self.shift_scheduler = shift_scheduler
        self.employee = employee
        self.logout_callback = logout_callback

        self.selected_week = tk.StringVar()
        self.week_options = self.get_week_start_dates()
        if self.week_options:
            self.selected_week.set(self.week_options[0])

        week_label = tk.Label(root, text="Select Week:")
        week_label.grid(row=0, column=0, padx=5, pady=5)

        week_menu = ttk.Combobox(root, textvariable=self.selected_week, values=self.week_options)
        week_menu.grid(row=0, column=1, padx=5, pady=5)
        week_menu.bind("<<ComboboxSelected>>", self.update_schedule)

        refresh_button = tk.Button(root, text="Refresh Schedule", command=self.update_schedule)
        refresh_button.grid(row=0, column=2, padx=5, pady=5)

        assign_button = tk.Button(root, text="Assign Shifts", command=self.assign_shifts)
        assign_button.grid(row=0, column=3, padx=5, pady=5)

        logout_button = tk.Button(root, text="Logout", command=self.logout)
        logout_button.grid(row=0, column=5, padx=5, pady=5)

        self.shift_labels = {}
        self.create_shift_table()

        self.update_schedule()

    def get_logged_in_employee(self):
        for emp in self.shift_scheduler.employees:
            if emp.user_id == self.shift_scheduler.current_user_id:
                return emp
        return None

    def open_constraints_window(self):
        employee = self.get_logged_in_employee()
        if not employee:
            tk.messagebox.showerror("Error", "No employee logged in.")
            return

        constraints_window = tk.Toplevel(self.root)
        constraints_window.title("Submit Constraints")
        ConstraintManager(constraints_window, employee)

    def create_shift_table(self):
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        shift_types = ["Morning", "Evening", "Night"]

        for col, day in enumerate(days):
            tk.Label(self.root, text=day, font=("Arial", 10, "bold")).grid(row=1, column=col + 1, padx=5, pady=5)

        for row, shift_type in enumerate(shift_types):
            tk.Label(self.root, text=shift_type, font=("Arial", 10, "bold")).grid(row=row + 2, column=0, padx=5, pady=5)

            for col, day in enumerate(days):
                label = tk.Label(self.root, text="--", borderwidth=1, relief="solid", width=18, height=2)
                label.grid(row=row + 2, column=col + 1, padx=5, pady=5)
                self.shift_labels[(day, shift_type)] = label


    def update_schedule(self, event=None):
        selected_week = self.selected_week.get()

        print(f"🔍 Checking shifts for week: {selected_week}")
        print(f"📂 Current shifts in memory: {[s.__dict__ for s in self.shift_scheduler.shifts]}")

        for label in self.shift_labels.values():
            label.config(text="--")

        week_shifts = [s for s in self.shift_scheduler.shifts if self.shift_scheduler.is_in_week(s.date, selected_week)]

        if not week_shifts:
            print(f"⚠️ No shifts found for {selected_week} in memory.")
        else:
            for shift in week_shifts:
                print(
                    f"✅ Found shift: {shift.date}, {shift.shift_type}, Employees: {[e.full_name for e in shift.employees]}")

        for shift in week_shifts:
            shift_date = shift.date
            shift_type = shift.shift_type
            day_name = self.get_day_name(shift_date)

            if (day_name, shift_type) in self.shift_labels:
                employees_text = "\n".join([emp.full_name for emp in shift.employees]) or "--"
                self.shift_labels[(day_name, shift_type)].config(text=employees_text)

    def assign_shifts(self):
        selected_week = self.selected_week.get()
        self.shift_scheduler.assign_shifts(selected_week)
        self.update_schedule()

    def logout(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass

        if self.logout_callback:
            self.logout_callback()

    @staticmethod
    def get_day_name(date_str):
        from datetime import datetime
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%A")

    def get_week_start_dates(self):
        start_dates = set()
        for shift in self.shift_scheduler.shifts:
            shift_date = datetime.strptime(shift.date, "%d/%m/%Y")
            week_start = shift_date - timedelta(days=(shift_date.weekday() + 1) % 7)
            start_dates.add(week_start.strftime("%d/%m/%Y"))

        return sorted(start_dates)
