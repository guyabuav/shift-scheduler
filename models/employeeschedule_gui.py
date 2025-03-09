import tkinter as tk
from tkinter import ttk


class EmployeeScheduleGUI:
    def __init__(self, root, shift_scheduler, username, logout_callback):
        self.root = root
        self.root.title(f"Schedule - {username}")
        self.shift_scheduler = shift_scheduler
        self.username = username
        self.logout_callback = logout_callback  # פונקציה להתנתקות

        # יצירת מסגרת ראשית
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # יצירת טבלת משמרות
        self.tree = ttk.Treeview(main_frame, columns=("Date", "Shift"), show="headings", height=10)
        self.tree.heading("Date", text="Date")
        self.tree.heading("Shift", text="Shift")
        self.tree.column("Date", anchor="center", width=120)
        self.tree.column("Shift", anchor="center", width=120)
        self.tree.pack(pady=10)

        # מסגרת לבחירת שבוע וכפתור רענון
        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(pady=5)

        # תפריט בחירת שבוע
        self.selected_week = tk.StringVar()
        self.week_options = list(set([s.date for s in shift_scheduler.shifts]))  # רשימת כל התאריכים בהם יש משמרות
        self.week_options.sort()  # מיון תאריכים
        if self.week_options:
            self.selected_week.set(self.week_options[0])

        week_menu = ttk.Combobox(controls_frame, textvariable=self.selected_week, values=self.week_options,
                                 state="readonly")
        week_menu.pack(side="left", padx=5)
        week_menu.bind("<<ComboboxSelected>>", self.update_schedule)

        # כפתור רענון
        refresh_button = tk.Button(controls_frame, text="Refresh", command=self.update_schedule)
        refresh_button.pack(side="left", padx=5)

        # כפתור Logout (מופרד מהשאר)
        logout_button = tk.Button(main_frame, text="Logout", command=self.logout, fg="white", bg="red",
                                  font=("Arial", 10, "bold"))
        logout_button.pack(pady=10, fill="x")

        # מילוי ראשוני של הטבלה
        self.update_schedule()

    def update_schedule(self, event=None):
        """ מעדכן את הטבלה עם המשמרות של העובד המחובר """
        selected_week = self.selected_week.get()

        # ניקוי כל הנתונים בטבלה
        self.tree.delete(*self.tree.get_children())

        # בדיקה אם יש משמרות בשבוע הנבחר
        if not selected_week:
            return

        # שליפת המשמרות של העובד מהשבוע הנבחר
        employee_shifts = self.shift_scheduler.get_employee_shifts(self.username, selected_week)

        if not employee_shifts:
            self.tree.insert("", "end", values=("No shifts", ""))
        else:
            for shift in employee_shifts:
                self.tree.insert("", "end", values=(shift.date, shift.shift_type))

    def logout(self):
        """ התנתקות מהממשק וחזרה למסך ההתחברות """
        try:
            self.root.destroy()  # סוגר את החלון הנוכחי
        except tk.TclError:
            pass  # אם החלון כבר סגור, התעלם מהשגיאה

        if self.logout_callback:
            self.logout_callback()  # מחזיר למסך ההתחברות


