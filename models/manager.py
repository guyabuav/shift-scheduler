from models.employee import Employee
from models.person import Person


class Manager(Employee, Person):
    def __init__(self, full_name, person_id, phone_number, email, employee_number, user_id, password, constraints=None):
        super().__init__(full_name, person_id, phone_number, email, employee_number, user_id, password, constraints)

    def modify_shift(self, shift_list, action, employee_list):
        for i, shift in enumerate(shift_list):
            print(f"{i + 1}. {shift}")

        shift_index = int(input("Select shift number")) - 1
        selected_shift = shift_list[shift_index]

        if action == "add":
            for i, employee in enumerate(employee_list):
                print(f"{i + 1}. {employee}")
            employee_index = int(input("Select employee number ")) - 1
            selected_employee = employee_list[employee_index]
            shift.add_employee(selected_employee) # what happens if employee already on shift? if there is maximum employees?
        elif action == "remove":
            for i, employee in enumerate(shift.employees):
                print(f"{i + 1}. {employee}")
            employee_index = int(input("Select employee number ")) - 1
            selected_employee = employee_list[employee_index]
            shift.remove_employee(selected_employee)
        else:
            print("Invalid action")
