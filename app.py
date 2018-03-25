import datetime
import ControllerOperator

"""
Main app file for Conference Database Generator
"""

insert_controller = ControllerOperator.ControllerOperator('mszarek_a')
date = datetime.datetime(2019, 1, 1, 0, 0, 0)
insert_controller.insert_participants(1000)
insert_controller.generate_conferences(200, date)
insert_controller.insert_individuals(100)
insert_controller.insert_companies(100)
insert_controller.generate_company_bookings(100)
insert_controller.generate_individual_bookings(100)
insert_controller.close()
