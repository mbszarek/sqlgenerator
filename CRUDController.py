import pyodbc
import datetime
from faker import Faker
import Getname
import random
import string
from os import getenv

"""
CRUD Controller class, responsible for basic CRUD operations on our database.
"""


class Controller:
    hostname = ''
    login = ''
    password = ''
    database_name = ''
    conn = ''
    cursor = ''
    fake = ''

    def __init__(self, database_name):
        self.fake = Faker()
        self.hostname = getenv('MSSQL_HOSTNAME')
        self.login = getenv('MSSQL_LOGIN')
        self.password = getenv('MSSQL_PASSWORD')
        self.database_name = database_name
        driver = '{ODBC Driver 13 for SQL Server}'
        format_string = 'DRIVER={};SERVER={};PORT=1433;DATABASE={};UID={};PWD={};'
        self.conn = pyodbc.connect(format_string.format(driver, self.hostname, self.database_name, self.login,
                                                        self.password))
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def get_all_customers(self):
        return_list = []
        select_statement = 'SELECT * FROM Customers'
        self.cursor.execute(select_statement)
        row = self.cursor.fetchone()
        while row:
            return_list.append(row)
            row = self.cursor.fetchone()
        return return_list

    def get_all_workshops(self):
        return_list = []
        select_statement = 'SELECT * FROM Workshops'
        self.cursor.execute(select_statement)
        for row in self.cursor:
            workshop_new = Workshop.Workshop(row.WorkshopID, row.Name, row.StartTime, row.EndTime, row.Description,
                                             row.Canceled, row.Free, row.Price, row.MaxCapacity, row.ConferenceDayID)
            return_list.append(workshop_new)
        return return_list

    def get_all_participants(self):
        select_statement = 'SELECT * FROM Participants'
        self.cursor.execute(select_statement)
        return self.cursor.fetchall()

    def get_random_company_id(self):
        select_statement = 'SELECT TOP 1 * FROM Companies ORDER BY NEWID()'
        self.cursor.execute(select_statement)
        return self.cursor.fetchone().CustomerID

    def get_random_individual_id(self):
        select_statement = 'SELECT TOP 1 * FROM Individuals ORDER BY NEWID()'
        self.cursor.execute(select_statement)
        return self.cursor.fetchone().CustomerID

    def get_all_conferences(self):
        return_list = []
        select_statement = 'SELECT * FROM Conferences'
        self.cursor.execute(select_statement)
        for row in self.cursor:
            conference_new = Conference.Conference(row[0], row[1], row[2], row[3], row[4], row[5])
            return_list.append(conference_new)
        return return_list

    def create_participant(self):
        names = Getname.get_address()
        first_name = names['name']['first']
        last_name = names['name']['last']
        insert_statement = 'INSERT INTO Participants (FirstName, LastName) VALUES (\'{}\', \'{}\')'
        self.cursor.execute(insert_statement.format(first_name, last_name))
        self.cursor.commit()

    def get_conference_id(self, start_date, end_date):
        select_statement = 'SELECT TOP 1 ConferenceID FROM Conferences WHERE StartDate = \'{}\' AND EndDate = \'{}\''
        self.cursor.execute(select_statement.format(start_date.strftime('%Y-%m-%d %H:%M:%S'),
                                                    end_date.strftime('%Y-%m-%d %H:%M:%S')))
        return self.cursor.fetchone().ConferenceID

    def create_conference(self, name, description, date, priceperdate):
        insert_statement = 'INSERT INTO Conferences (Name, Description, StartDate, EndDate, PricePerDate) VALUES ' \
                           '(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\')'
        random_number = random.randint(2, 4)
        delta = datetime.timedelta(days=random_number)
        enddate = date + delta
        self.cursor.execute(insert_statement.format(name, description, date.strftime('%Y-%m-%d'),
                                                    enddate.strftime('%Y-%m-%d'), priceperdate))
        self.cursor.commit()
        conference_id = self.get_conference_id(date, enddate)
        discount_number = random.randint(2, 8)
        self.create_discounts(conference_id, discount_number)
        select_conferencedayid = 'SELECT * FROM  ConferenceDays WHERE ConferenceID = {}'
        for single_day in (date + datetime.timedelta(n) for n in range(random_number)):
            self.create_conference_day(conference_id, single_day)
            self.cursor.execute(select_conferencedayid.format(conference_id))
            conferencedays = self.cursor.fetchall()
            for conferenceday in conferencedays:
                workshop_date = datetime.datetime.combine(datetime.date.today(), datetime.time(10, 0, 0))
                for i in range(4):
                    self.create_workshop(''.join(self.fake.company().split(',')), self.fake.text(), workshop_date, random.randint(5, 10) *
                                         10, conferenceday.ConferenceDayID)
                    workshop_date += datetime.timedelta(hours=2)

    def create_customer(self, email, phone, country, city, address):
        insert_text = 'INSERT INTO Customers (Email, Phone, Country, City, Address) VALUES ' \
                      '(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\')'
        self.cursor.execute(insert_text.format(email, phone, country, city, address))
        self.cursor.commit()

    def get_customer_id(self, email, phone, address):
        select_text = 'SELECT TOP 1 CustomerID FROM Customers WHERE Email = \'{}\' AND Phone = \'{}\' AND Address =' \
                      ' \'{}\''
        self.cursor.execute(select_text.format(email, phone, address))
        return self.cursor.fetchone().CustomerID

    def create_company(self):
        company = Getname.get_company()
        address = Getname.get_address()
        company_name = company['company']
        company_email = company['email_u'] + '@' + company['email_d']
        company_phone = ''.join(random.choice(string.digits) for i in range(9))
        company_address = address['location']['street']
        company_country = address['nat']
        company_city = address['location']['city']
        company_nip = company_country + ''.join(random.choice(string.digits) for i in range(10))
        self.create_customer(company_email, company_phone, company_country, company_city, company_address)
        customer_id = self.get_customer_id(company_email, company_phone, company_address)
        insert_text = 'INSERT INTO Companies (CompanyName, NIP, CustomerID) VALUES (\'{}\', \'{}\', \'{}\')'
        self.cursor.execute(insert_text.format(company_name, company_nip, customer_id))
        self.cursor.commit()

    def create_individual(self):
        individual = Getname.get_company()
        address = Getname.get_address()
        firstname = address['name']['first']
        lastname = address['name']['last']
        email = individual['email_u'] + '@' + individual['email_d']
        phone = ''.join(random.choice(string.digits) for i in range(9))
        country = address['nat']
        city = address['location']['city']
        address = ' '.join(address['location']['street'].split('\n'))
        self.create_customer(email, phone, country, city, address)
        customer_id = self.get_customer_id(email, phone, address)
        insert_text = 'INSERT INTO Individuals (FirstName, LastName, CustomerID) VALUES (\'{}\', \'{}\', \'{}\')'
        self.cursor.execute(insert_text.format(firstname, lastname, customer_id))
        self.cursor.commit()

    def create_workshop(self, name, description, date, priceperdate, conference_day_id):
        insert_statement = 'INSERT INTO Workshops (Name, StartTime, EndTime, Description, Price, ConferenceDayID) ' \
                           'VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')'
        duration = 90
        delta = datetime.timedelta(minutes=duration)
        enddate = date + delta
        self.cursor.execute(insert_statement.format(name, date.strftime('%H:%M:%S'),
                                                    enddate.strftime('%H:%M:%S'), description, priceperdate,
                                                    conference_day_id))
        self.cursor.commit()

    def create_conference_booking(self, customer_id):
        self.cursor.execute('SELECT TOP 1 * FROM Conferences ORDER BY NEWID()')
        day_conference_id = self.cursor.fetchone().ConferenceID
        quantity = random.randint(2, 6) * 10
        insert_text = 'INSERT INTO DayBookings (Quantity, CustomerID, ConferenceDayID) VALUES (\'{}\', \'{}\', \'{}\')'
        self.cursor.execute(insert_text.format(quantity, customer_id, day_conference_id))
        self.cursor.commit()
        self.cursor.execute('SELECT TOP 1 * FROM DayBookings WHERE ConferenceDayID = {} AND CustomerID = {}'.format(
            day_conference_id, customer_id))
        day_booking_id = self.cursor.fetchone().DayBookingID
        select_participants = 'SELECT TOP {} * FROM Participants ORDER BY NEWID()'
        self.cursor.execute(select_participants.format(quantity))
        participants = self.cursor.fetchall()
        insert_day_participant = 'INSERT INTO DayParticipants (DayBookingID, ParticipantID) VALUES ({}, {})'
        for i in participants:
            self.cursor.execute(insert_day_participant.format(day_booking_id, i.ParticipantID))
            self.cursor.commit()
        select_workshops = 'SELECT * FROM Workshops WHERE ConferenceDayID = {}'
        select_day_participants = 'SELECT TOP {} * FROM DayParticipants WHERE DayBookingID = {}'
        insert_workshop_booking = 'INSERT INTO WorkshopBookings (Quantity, WorkshopID, DayBookingID, CustomerID) ' \
                                  'VALUES ({}, {}, {}, {})'
        insert_workshop_participant = 'INSERT INTO WorkshopParticipants (WorkshopBookingsID, ParticipantID) ' \
                                      'VALUES ({}, {})'
        get_workshop_booking_id = 'SELECT TOP 1 * FROM WorkshopBookings WHERE WorkshopID = {} AND DayBookingID = {} ' \
                                  'AND CustomerID = {}'
        self.cursor.execute(select_workshops.format(day_conference_id, day_booking_id))
        workshops = self.cursor.fetchall()
        for workshop in workshops:
            self.cursor.execute(insert_workshop_booking.format(quantity, workshop.WorkshopID, day_booking_id,
                                                               customer_id))
            self.cursor.commit()
            self.cursor.execute(select_day_participants.format(min(workshop.MaxCapacity, quantity), day_booking_id))
            day_participants = self.cursor.fetchall()
            self.cursor.execute(get_workshop_booking_id.format(workshop.WorkshopID, day_booking_id, customer_id))
            curr_workshop_booking_id = self.cursor.fetchone().WorkshopBookingsID
            for p in day_participants:
                self.cursor.execute(insert_workshop_participant.format(curr_workshop_booking_id, p.ParticipantID))

    def create_conference_day(self, conference_id, single_day):
        insert_statement = 'INSERT INTO ConferenceDays (ConferenceID, Date) VALUES (\'{}\', \'{}\')'
        self.cursor.execute(insert_statement.format(conference_id, single_day.strftime('%Y-%m-%d %H:%M:%S')))
        self.cursor.commit()

    def create_discounts(self, conference_id, n):
        insert_statement = 'INSERT INTO Discounts (DiscountPercent, DaysUntilConference, ConferenceID) VALUES (\'{}\',' \
                           '\'{}\', \'{}\')'
        basic_discount = random.randint(4, 8)
        basic_days = 30
        for i in range(n):
            discount = basic_discount * (i + 1)
            days = basic_days * (i + 1)
            self.cursor.execute(insert_statement.format(discount, days, conference_id))
            self.cursor.commit()
