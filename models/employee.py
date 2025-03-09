import json
import os
from models.person import Person


class Employee(Person):
    def __init__(self, full_name, person_id, phone_number, email, employee_number, user_id, password, constraints=None):
        super().__init__(full_name, person_id, phone_number, email)
        self.employee_number = employee_number
        self.user_id = user_id
        self.password = password
        self.constraints = constraints if constraints else {}  # מילון של אילוצים לפי שבועות
        self.load_constraints_from_file()  # טוען אילוצים מהקובץ אם קיימים

    def add_constraint(self, week_start, day, shift_type):
        """ מוסיף אילוץ עבור שבוע מסוים """
        if week_start not in self.constraints:
            self.constraints[week_start] = {}  # יצירת מילון עבור השבוע
        if day not in self.constraints[week_start]:
            self.constraints[week_start][day] = []
        if shift_type not in self.constraints[week_start][day]:  # 🔹 מניעת כפילויות
            self.constraints[week_start][day].append(shift_type)
            self.save_constraints_to_file()  # 🔹 שמירה לקובץ רק אם נוסף אילוץ חדש

    def submit_constraints(self, week_start_date, constraints):
        """ 🔹 מעדכן אילוצים ישירות למערכת ומיד שומר לקובץ """
        self.constraints[week_start_date] = constraints
        self.save_constraints_to_file()
        print(f"✅ Constraints submitted for {self.full_name} in the week of {week_start_date}")

    def __str__(self):
        return super().__str__() + f"Employee Number: {self.employee_number}, User Id: {self.user_id}, Constraints: {self.constraints}"

    def save_constraints_to_file(self):
        """ 🔹 שומר את האילוצים לקובץ JSON גלובלי במקום קובץ לכל עובד בנפרד """
        file_path = "constraints.json"
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    all_constraints = json.load(file)
            else:
                all_constraints = {}

            all_constraints[self.user_id] = self.constraints  # 🔹 שמירה לפי ID משתמש

            with open(file_path, "w") as file:
                json.dump(all_constraints, file, indent=4)
            print(f"✅ Constraints saved for {self.full_name} ({self.user_id})")
        except Exception as e:
            print(f"❌ Error saving constraints: {e}")

    def load_constraints_from_file(self):
        """ 🔹 טוען אילוצים מקובץ JSON גלובלי לפי ה- `user_id` """
        file_path = "constraints.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as file:
                    data = file.read().strip()  # קריאה ובדיקה אם הקובץ ריק
                    if not data:
                        print(f"⚠️ Warning: {file_path} is empty!")
                        return  # הקובץ קיים אך ריק, לא נבצע טעינה

                    all_constraints = json.loads(data)  # טעינה מבוקרת
                    print(f"📂 Loaded constraints file: {all_constraints}")  # 🔹 בדיקה שהמידע קיים

                    if self.user_id in all_constraints:
                        self.constraints = all_constraints[self.user_id]
                        print(f"✅ Constraints loaded for {self.full_name}: {self.constraints}")
                        print(f"DEBUG - {self.full_name} constraints: {self.constraints}")

                    else:
                        print(f"⚠️ No constraints found for {self.user_id}")
            except json.JSONDecodeError as e:
                print(f"❌ Error: Invalid JSON format in {file_path}: {e}")
            except Exception as e:
                print(f"⚠️ Error loading constraints: {e}")
