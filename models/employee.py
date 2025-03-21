import json
import os
from models.person import Person


class Employee(Person):
    def __init__(self, full_name, person_id, phone_number, email, employee_number, user_id, password, constraints=None):
        super().__init__(full_name, person_id, phone_number, email)
        self.employee_number = employee_number
        self.user_id = user_id
        self.password = password
        self.constraints = constraints if constraints else {}
        self.load_constraints_from_file()

    def add_constraint(self, week_start, day, shift_type):
        if week_start not in self.constraints:
            self.constraints[week_start] = {}
        if day not in self.constraints[week_start]:
            self.constraints[week_start][day] = []
        if shift_type not in self.constraints[week_start][day]:
            self.constraints[week_start][day].append(shift_type)
            self.save_constraints_to_file()

    def submit_constraints(self, week_start_date, constraints):
        self.constraints[week_start_date] = constraints
        self.save_constraints_to_file()

    def __str__(self):
        return super().__str__() + f"Employee Number: {self.employee_number}, User Id: {self.user_id}, Constraints: {self.constraints}"

    def save_constraints_to_file(self):
        file_path = "constraints.json"
        try:
            all_constraints = {}

            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    try:
                        all_constraints = json.load(file)
                    except json.JSONDecodeError:
                        all_constraints = {}

            all_constraints[self.user_id] = self.constraints

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(all_constraints, file, indent=4)

            print(
                f"✅ Constraints saved for {self.full_name} ({self.user_id}): {json.dumps(self.constraints, indent=4)}")

        except Exception as e:
            print(f"❌ Error saving constraints: {e}")

    def load_constraints_from_file(self):
        file_path = "constraints.json"

        if not os.path.exists(file_path):
            print(f"⚠️ Warning: {file_path} does not exist! Creating new.")
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump({}, file)
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = file.read().strip()
                if not data:
                    self.constraints = {}
                    return

                all_constraints = json.loads(data)

                user_id_str = str(self.user_id)
                if user_id_str in all_constraints:
                    self.constraints = all_constraints[user_id_str]
                    print(f"✅ Constraints loaded for {self.full_name}: {json.dumps(self.constraints, indent=4)}")
                else:
                    self.constraints = {}

        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON format in {file_path}: {e}")
        except Exception as e:
            print(f"⚠️ Error loading constraints: {e}")
