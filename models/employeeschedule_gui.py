import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from models.constraint_gui import ConstraintManager


class EmployeeScheduleGUI:
    def __init__(self, root, shift_scheduler, username, logout_callback):
        self.root = root
        self.root.title(f"Schedule - {username}")
        self.shift_scheduler = shift_scheduler
        self.username = username
        self.logout_callback = logout_callback

        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(main_frame, columns=("Date", "Shift"), show="headings", height=10)
        self.tree.heading("Date", text="Date")
        self.tree.heading("Shift", text="Shift")
        self.tree.column("Date", anchor="center", width=120)
        self.tree.column("Shift", anchor="center", width=120)
        self.tree.pack(pady=10)

        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(pady=5)

        self.selected_week = tk.StringVar()
        self.week_options = self.get_week_start_dates()
        self.week_options.sort()
        if self.week_options:
            self.selected_week.set(self.week_options[0])

        week_menu = ttk.Combobox(controls_frame, textvariable=self.selected_week, values=self.week_options,
                                 state="readonly")
        week_menu.pack(side="left", padx=5)
        week_menu.bind("<<ComboboxSelected>>", self.update_schedule)

        refresh_button = tk.Button(controls_frame, text="Refresh", command=self.update_schedule)
        refresh_button.pack(side="left", padx=5)

        constraints_button = tk.Button(controls_frame, text="Submit Constraints", command=self.open_constraints_window)
        constraints_button.pack(side="left", padx=5)

        logout_button = tk.Button(main_frame, text="Logout", command=self.logout, fg="white", bg="red",
                                  font=("Arial", 10, "bold"))
        logout_button.pack(pady=10, fill="x")

        self.update_schedule()

    def update_schedule(self, event=None):
        selected_week = self.selected_week.get()

        self.tree.delete(*self.tree.get_children())

        if not selected_week:
            return

        employee_shifts = self.shift_scheduler.get_employee_shifts(self.username, selected_week)

        if not employee_shifts:
            self.tree.insert("", "end", values=("No shifts", ""))
        else:
            for shift in employee_shifts:
                self.tree.insert("", "end", values=(shift.date, shift.shift_type))

    def logout(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass

        if self.logout_callback:
            self.logout_callback()

    def get_week_start_dates(self):
        start_dates = set()
        for shift in self.shift_scheduler.shifts:
            shift_date = datetime.strptime(shift.date, "%d/%m/%Y")
            week_start = shift_date - timedelta(days=(shift_date.weekday() + 1) % 7)
            start_dates.add(week_start.strftime("%d/%m/%Y"))

        return sorted(start_dates)

    def open_constraints_window(self):
        constraints_window = tk.Toplevel(self.root)
        constraints_window.title("Submit Constraints")
        employee = self.get_logged_in_employee()
        if not employee:
            tk.messagebox.showerror("Error", "No employee found.")
            return

        ConstraintManager(constraints_window, employee)

    def get_logged_in_employee(self):
        for emp in self.shift_scheduler.employees:
            if emp.user_id == self.username:  # בדיקה לפי user_id
                return emp
        return None
