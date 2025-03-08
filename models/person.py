class Person:
    def __init__(self, full_name, person_id, phone_number, email):
        self.full_name = full_name
        self.person_id = person_id
        self.phone_number = phone_number
        self.email = email

    def __str__(self):
        return f"Name: {self.full_name}, Id: {self.person_id}, Phone Number: {self.phone_number}, Email: {self.email}"

