import pyodbc
import CRUDController
import datetime
import random
from faker import Faker

"""
Controller Operator class, it's responsible for generating huge amount of data.
"""


class ControllerOperator:
    controller = ''
    fake = ''

    def __init__(self, db):
        self.controller = CRUDController.Controller(db)
        self.fake = Faker()

    def close(self):
        self.controller.close()

    def insert_participants(self, amount):
        for i in range(amount):
            try:
                self.controller.create_participant()
            except pyodbc.ProgrammingError:
                print('Weird name')
            except pyodbc.IntegrityError:
                print('Constraint')

    def insert_companies(self, amount):
        for i in range(amount):
            try:
                self.controller.create_company()
            except pyodbc.ProgrammingError:
                print('Weird name')
            except pyodbc.IntegrityError:
                print('Constraint')

    def insert_individuals(self, amount):
        for i in range(amount):
            try:
                self.controller.create_individual()
            except pyodbc.ProgrammingError:
                print('Weird name')
            except pyodbc.IntegrityError:
                print('Constraint')

    def get_all_customers(self):
        return self.controller.get_all_customers()

    def get_all_workshops(self):
        return self.controller.get_all_workshops()

    def get_all_participants(self):
        return self.controller.get_all_participants()

    def get_all_conferences(self):
        return self.controller.get_all_conferences()

    def insert_conference(self, date):
        name = self.fake.company()
        name = ''.join(name.split(','))
        print(name)
        description = self.fake.text()
        price_per_date = random.randint(5, 10) * 10
        self.controller.create_conference(name, description, date, price_per_date)

    def generate_conferences(self, n, start_date):
        date = start_date
        for i in range(n):
            self.insert_conference(date)
            date += datetime.timedelta(days=random.randint(15, 18))

    def create_company_booking(self):
        company_id = self.controller.get_random_company_id()
        self.controller.create_conference_booking(company_id)

    def generate_company_bookings(self, n):
        for i in range(n):
            self.create_company_booking()

    def create_individual_booking(self):
        individual_id = self.controller.get_random_individual_id()
        self.controller.create_conference_booking(individual_id)

    def generate_individual_bookings(self, n):
        for i in range(n):
            self.create_individual_booking()
