import tkinter as tk
from tkinter import ttk
from datetime import datetime
from models.shiftscheduler import ShiftScheduler
from models.employee import Employee


class ShiftSchedulerGUI:
    def __init__(self, root, shift_scheduler):
        self.root = root
        self.root.title("Shift Scheduler")

        self.shift_scheduler = shift_scheduler
        self.selected_week = tk.StringVar()
        self.week_options = ["02/03/2025", "09/03/2025"]
        self.selected_week.set(self.week_options[0])

        # תפריט בחירת שבוע
        week_label = tk.Label(root, text="Select Week:")
        week_label.grid(row=0, column=0, padx=5, pady=5)

        week_menu = ttk.Combobox(root, textvariable=self.selected_week, values=self.week_options)
        week_menu.grid(row=0, column=1, padx=5, pady=5)
        week_menu.bind("<<ComboboxSelected>>", self.update_schedule)

        # כפתור לרענון התצוגה
        refresh_button = tk.Button(root, text="Refresh Schedule", command=self.update_schedule)
        refresh_button.grid(row=0, column=2, padx=5, pady=5)

        # כפתור לשיבוץ אוטומטי
        assign_button = tk.Button(root, text="Assign Shifts", command=self.assign_shifts)
        assign_button.grid(row=0, column=3, padx=5, pady=5)

        # יצירת טבלה חדשה: 3 שורות (בוקר/ערב/לילה) × 7 עמודות (ימים א'-ש')
        self.shift_labels = {}  # מילון לשמירת הפניות לכל משבצת בטבלה
        self.create_shift_table()

        # מילוי ראשוני של הנתונים
        self.update_schedule()

    def create_shift_table(self):
        """יוצר טבלה מותאמת אישית של משמרות (3x7)"""
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        shift_types = ["Morning", "Evening", "Night"]

        # כותרות הימים
        for col, day in enumerate(days):
            tk.Label(self.root, text=day, font=("Arial", 10, "bold")).grid(row=1, column=col + 1, padx=5, pady=5)

        # יצירת המשבצות בטבלה
        for row, shift_type in enumerate(shift_types):
            # תווית שם המשמרת בצד שמאל
            tk.Label(self.root, text=shift_type, font=("Arial", 10, "bold")).grid(row=row + 2, column=0, padx=5, pady=5)

            for col, day in enumerate(days):
                label = tk.Label(self.root, text="--", borderwidth=1, relief="solid", width=18, height=2)
                label.grid(row=row + 2, column=col + 1, padx=5, pady=5)
                self.shift_labels[(day, shift_type)] = label  # שמירת הפנייה לכל תא

    def update_schedule(self, event=None):
        """ מעדכן את הטבלה עם שמות העובדים המשובצים לכל משמרת """
        selected_week = self.selected_week.get()

        # ניקוי כל התאים בטבלה
        for label in self.shift_labels.values():
            label.config(text="--")

        # מילוי המשמרות מהשבוע שנבחר
        week_shifts = [s for s in self.shift_scheduler.shifts if self.shift_scheduler.is_in_week(s.date, selected_week)]

        for shift in week_shifts:
            shift_date = shift.date
            shift_type = shift.shift_type
            day_name = self.get_day_name(shift_date)  # המרת התאריך לשם היום

            if (day_name, shift_type) in self.shift_labels:
                employees_text = "\n".join([emp.full_name for emp in shift.employees]) or "--"
                self.shift_labels[(day_name, shift_type)].config(text=employees_text)

    def assign_shifts(self):
        """ מבצע שיבוץ אוטומטי לשבוע הנבחר """
        selected_week = self.selected_week.get()
        self.shift_scheduler.assign_shifts(selected_week)
        self.update_schedule()  # ריענון התצוגה


    @staticmethod
    def get_day_name(date_str):
        from datetime import datetime
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%A")