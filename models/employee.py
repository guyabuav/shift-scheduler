from models.person import Person


class Employee(Person):
    def __init__(self, full_name, person_id, phone_number, email, employee_number, user_id, password, constraints):
        super().__init__(full_name, person_id, phone_number, email)
        self.employee_number = employee_number
        self.user_id = user_id
        self.password = password
        self.constraints = {}

    def add_constraint(self, day, shift_type):
        if day not in self.constraints:
            self.constraints[day] = []
        self.constraints[day].append(shift_type)

        def submit_constraints(self, employee, week_start_date, constraints):
            """ מוסיף אילוצים לעובד עבור שבוע מסוים """
            if employee not in self.employees:
                print(f"❌ Employee {employee.full_name} not found!")
                return

            employee.constraints[week_start_date] = constraints
            print(f"✅ Constraints submitted for {employee.full_name} in the week of {week_start_date}")

    def __str__(self):
        return super().__str__() + f"Employee Numer: {self.employee_number}, User Id: {self.user_id}, Constraints: {self.constraints}"
