import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json


class ConstraintManager:
    def __init__(self, master, employee):
        self.checkbuttons = None
        self.master = master
        self.employee = employee
        self.week_constraints = {}

        self.master.title(f"Submit Constraints - {self.employee.full_name}")

        self.week_label = tk.Label(master, text="Select week start date (DD/MM/YYYY):")
        self.week_label.pack()

        self.week_entry = tk.Entry(master)
        self.week_entry.pack()

        self.load_week_button = tk.Button(master, text="Load Week", command=self.load_week)
        self.load_week_button.pack()

        self.table_frame = tk.Frame(master)
        self.table_frame.pack()

        self.save_button = tk.Button(master, text="Save Constraints", command=self.save_constraints)
        self.save_button.pack()

    def load_week(self):
        week_start_date = self.week_entry.get()
        try:
            base_date = datetime.strptime(week_start_date, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use DD/MM/YYYY.")
            return

        self.week_constraints = self.employee.constraints.get(week_start_date, {})

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        shift_types = ["Morning", "Evening", "Night"]

        for col, shift in enumerate(["Day"] + shift_types):
            label = tk.Label(self.table_frame, text=shift, borderwidth=1, relief="solid", width=12)
            label.grid(row=0, column=col)

        self.checkbuttons = {}

        for row, day in enumerate(days):
            label = tk.Label(self.table_frame, text=day, borderwidth=1, relief="solid", width=12)
            label.grid(row=row + 1, column=0)

            for col, shift in enumerate(shift_types):
                var = tk.BooleanVar()
                checkbox = tk.Checkbutton(self.table_frame, bg="white", variable=var)
                checkbox.grid(row=row + 1, column=col + 1)

                if shift in self.week_constraints.get(day, []):
                    var.set(True)
                    checkbox.config(bg="red")

                self.checkbuttons[(day, shift)] = (checkbox, var)

    def save_constraints(self):
        week_start_date = self.week_entry.get()
        if not week_start_date:
            messagebox.showerror("Error", "Please enter a week start date.")
            return

        constraints = {}
        for (day, shift), (checkbox, var) in self.checkbuttons.items():
            if var.get():
                if day not in constraints:
                    constraints[day] = []
                constraints[day].append(shift)

        self.employee.submit_constraints(week_start_date, constraints)

        messagebox.showinfo("Success", "Constraints saved successfully!")
