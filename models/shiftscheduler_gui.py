import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime, timedelta
from models.constraint_gui import ConstraintManager
import json


class ShiftSchedulerGUI:
    def __init__(self, root, shift_scheduler, employee, logout_callback):
        self.remove_button = None
        self.add_button = None
        self.selected_shift = None
        self.shift_listbox = None
        self.edit_window = None
        self.root = root
        self.root.title("Shift Scheduler")

        self.shift_scheduler = shift_scheduler
        self.employee = employee
        self.logout_callback = logout_callback

        self.selected_week = tk.StringVar()

        self.week_options = sorted(
            self.get_week_start_dates(),
            key=lambda date_str: datetime.strptime(date_str, "%d/%m/%Y")
        )
        if self.week_options:
            self.selected_week.set(self.week_options[0])

        week_label = tk.Label(root, text="Select Week:")
        week_label.grid(row=0, column=0, padx=5, pady=5)

        week_menu = ttk.Combobox(root, textvariable=self.selected_week, values=self.week_options)
        week_menu.grid(row=0, column=1, padx=5, pady=5)
        week_menu.bind("<<ComboboxSelected>>", lambda event: self.update_schedule())

        refresh_button = tk.Button(root, text="Refresh Schedule", command=self.update_schedule)
        refresh_button.grid(row=0, column=2, padx=5, pady=5)

        assign_button = tk.Button(root, text="Assign Shifts", command=self.assign_shifts)
        assign_button.grid(row=0, column=3, padx=5, pady=5)

        self.edit_button = tk.Button(self.root, text="Edit Shift", command=self.open_edit_shift_window)
        self.edit_button.grid(row=0, column=4, padx=5, pady=5)

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

    def update_schedule(self):
        selected_week = self.selected_week.get()

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

    def open_edit_shift_window(self):
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Shift")

        self.selected_shift = None
        self.shift_listbox = tk.Listbox(self.edit_window, height=10, width=50)
        self.shift_listbox.pack()
        self.load_shifts()
        self.shift_listbox.bind("<<ListboxSelect>>", self.on_shift_selected)

        self.add_button = tk.Button(self.edit_window, text="Add Employee", command=self.add_employee)
        self.add_button.pack()

        self.remove_button = tk.Button(self.edit_window, text="Remove Employee", command=self.remove_employee)
        self.remove_button.pack()

    def load_shifts(self):
        self.shift_listbox.delete(0, tk.END)
        for shift in self.shift_scheduler.shifts:
            shift_info = f"{shift.date} - {shift.shift_type} ({len(shift.employees)}/{shift.max_employees})"
            self.shift_listbox.insert(tk.END, shift_info)

    def on_shift_selected(self, event=None):
        selection = self.shift_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_shift = self.shift_scheduler.shifts[index]
            self.show_shift_details()

    def show_shift_details(self):
        if not self.selected_shift:
            return

        employees = "\n".join([emp.full_name for emp in self.selected_shift.employees])
        messagebox.showinfo("Shift Details",
                            f"{self.selected_shift.date} - {self.selected_shift.shift_type}\nEmployees:\n{employees}")

    def add_employee(self):
        if not self.selected_shift:
            messagebox.showerror("Error", "No shift selected!")
            return

        employee_name = simpledialog.askstring("Add Employee", "Enter employee name:")
        if not employee_name:
            return

        employee = next((emp for emp in self.shift_scheduler.employees if emp.full_name == employee_name), None)
        if not employee:
            messagebox.showerror("Error", "Employee not found!")
            return

        if len(self.selected_shift.employees) >= self.selected_shift.max_employees:
            messagebox.showerror("Error", "Shift is already full!")
            return

        if employee in self.selected_shift.employees:
            messagebox.showerror("Error", "Employee already in this shift!")
            return

        if employee.user_id in [e.user_id for shift in self.shift_scheduler.shifts if
                                shift.date == self.selected_shift.date for e in shift.employees]:
            messagebox.showerror("Error", "Employee already has a shift that day!")
            return

        if self.shift_scheduler.has_constraint(employee, self.selected_shift, self.selected_shift.date):
            messagebox.showerror("Error", "Employee has a constraint for this shift!")
            return

        shift_date = datetime.strptime(self.selected_shift.date, "%d/%m/%Y")
        week_start = shift_date - timedelta(days=(shift_date.isoweekday() % 7))
        week_end = week_start + timedelta(days=6)

        print(f"🔍 Calculating shifts from {week_start.strftime('%d/%m/%Y')} to {week_end.strftime('%d/%m/%Y')}")

        total_shifts = 0
        try:
            with open("schedule.json", "r") as file:
                schedule_data = json.load(file)

            print(f"📂 Loaded schedule.json data: {schedule_data}")

            for shift in schedule_data:
                shift_date = datetime.strptime(shift["date"], "%d/%m/%Y")
                if week_start <= shift_date <= week_end:

                    if employee.user_id in shift["employees"]:
                        print(f"✅ Found shift for {employee.full_name} on {shift['date']} ({shift['shift_type']})")
                        total_shifts += 1


        except (FileNotFoundError, json.JSONDecodeError):
            print("⚠️ Warning: Unable to read schedule.json. Assuming no shifts assigned.")

        print(f"🔍 Total shifts for {employee.full_name} this week: {total_shifts}")

        if total_shifts >= 5:
            response = messagebox.askyesno("Warning", "Employee already has 5 shifts. Do you want to proceed?")
            if not response:
                return

        self.selected_shift.add_employee(employee)

        day_index = (datetime.strptime(self.selected_shift.date, "%d/%m/%Y").weekday() + 1) % 7
        shift_index = ["Morning", "Evening", "Night"].index(self.selected_shift.shift_type)

        print(f"Before adding: {self.shift_scheduler.workload_matrix[employee][day_index][shift_index]}")
        self.shift_scheduler.workload_matrix[employee][day_index][shift_index] += 1
        print(f"After adding: {self.shift_scheduler.workload_matrix[employee][day_index][shift_index]}")

        self.shift_scheduler.save_schedule_to_file()
        self.shift_scheduler.save_workload_matrix()

        messagebox.showinfo("Success", f"{employee.full_name} added to shift!")
        self.load_shifts()

    def remove_employee(self):
        if not self.selected_shift:
            messagebox.showerror("Error", "No shift selected!")
            return

        employee_name = simpledialog.askstring("Remove Employee", "Enter employee name:")
        if not employee_name:
            return

        employee = next((emp for emp in self.selected_shift.employees if emp.full_name == employee_name), None)
        if not employee:
            messagebox.showerror("Error", "Employee not found in this shift!")
            return

        self.selected_shift.remove_employee(employee)

        day_index = (datetime.strptime(self.selected_shift.date, "%d/%m/%Y").weekday() + 1) % 7
        shift_index = ["Morning", "Evening", "Night"].index(self.selected_shift.shift_type)
        self.shift_scheduler.workload_matrix[employee][day_index][shift_index] -= 1
        self.shift_scheduler.save_schedule_to_file()
        self.shift_scheduler.save_workload_matrix()

        if len(self.selected_shift.employees) == 0:
            messagebox.showwarning("Warning", "Shift has no employees left!")

        self.shift_scheduler.save_schedule_to_file()
        self.shift_scheduler.save_workload_matrix()

        messagebox.showinfo("Success", f"{employee.full_name} removed from shift!")
        self.load_shifts()
