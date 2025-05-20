import unittest
from app import create_app

from app.models import db, SerializedPart, Customer, ServiceTicket, PartDescription, Mechanic, Service
from datetime import datetime
from werkzeug.security import generate_password_hash

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.ticket = ServiceTicket(
            VIN= "VIN12345",
            id= 1,
            customer_id= 1,
            service_date= datetime.strptime("2025-05-15", "%Y-%m-%d").date(),
            service_desc= "Replace Brakes"
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.ticket)
            db.session.commit()
        self.mechanic = Mechanic(
            id=1,
            name="Test Mechanic",
            email="test@email.com",
            phone="123",
            salary=1,
            password=generate_password_hash("123")
        )
        with self.app.app_context():
            db.session.add(self.mechanic)
            db.session.commit()
        self.part_description = PartDescription(
                part_name= "all-season tire",
                id= 1,
                price= 100,
                brand= "Best Tires"
            )
        with self.app.app_context():
            db.session.add(self.part_description)
            db.session.commit()
        self.serialized_part = SerializedPart(
            id=1,
            part_id=1,
            ticket_id=None
            )
        with self.app.app_context():
            db.session.add(self.serialized_part)
            db.session.commit()
        self.customer = Customer(
            id=1,
            name="Test", 
            email="test@email.com", 
            phone="123-123-test", 
            password=generate_password_hash("123")
            )
        with self.app.app_context():
            db.session.add(self.customer)
            db.session.commit()
        self.service = Service(
            name="Test Service",
            labor_hours= 1,
           	labor_rate= 100,
            id=1
        )
        with self.app.app_context():
            db.session.add(self.service)
            db.session.commit()
        self.client = self.app.test_client()
        
    def test_create_ticket(self):
        ticket_payload = {
            "VIN": "TESTVIN1",
            "customer_id": 1,
            "service_desc": "replace brakes",
            "service_date": "2025-05-19"
        }

        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['VIN'], 'TESTVIN1')
        
    def test_invalid_creation(self):
        ticket_payload = {
            "VIN": "TESTVIN1",
            "customer_id": 1,
            "service_desc": "replace brakes"
        }

        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['service_date'], ['Missing data for required field.'])
        
    def test_part_update(self):
        update_payload = {
            "VIN": "TESTVIN1",
            "customer_id": 1,
            "service_desc": "replace brakes and tires",
            "service_date": "2025-05-19"
        }
        response = self.client.put('/service-tickets/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_desc'], 'replace brakes and tires')
        
    def test_get_tickets(self):
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['VIN'], 'VIN12345')
        
    def test_get_single_ticket(self):
        response = self.client.get('/service-tickets/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['VIN'], 'VIN12345')
        
    def test_invalid_get_single_ticket(self):
        response = self.client.get('/service-tickets/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid ticket_id.')
        
    def test_ticket_delete(self):
        response = self.client.delete('/service-tickets/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Succesfully deleted service Ticket 1')
        
    def test_invalid_part_delete(self):
        response = self.client.delete('/service-tickets/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'invalid ticket_id')
        
    def test_add_mechanic(self):
        response = self.client.put('/service-tickets/1/add-mechanic/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully added Test Mechanic to the ticket(order id: 1).')
        
    def test_invalid_add_mechanic_1(self):
        self.client.put('/service-tickets/1/add-mechanic/1')
        response = self.client.put('/service-tickets/1/add-mechanic/1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Test Mechanic already assigned to this ticket.')
        
    def test_invalid_add_mechanic_2(self):
        response = self.client.put('/service-tickets/1/add-mechanic/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid ticket_id or mechanic_id')
        
    def test_remove_mechanic(self):
        self.client.put('/service-tickets/1/add-mechanic/1')
        response = self.client.put('/service-tickets/1/remove-mechanic/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully removed Test Mechanic from the ticket(order id: 1).')
    
    def test_invalid_remove_mechanic_1(self):
        response = self.client.put('/service-tickets/1/remove-mechanic/1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Test Mechanic not assigned to ticket')
        
    def test_invalid_remove_mechanic_2(self):
        response = self.client.put('/service-tickets/1/remove-mechanic/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'invalid mechanic_id or ticket_id')  
    
    def test_add_part(self):
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully added one all-season tire to the ticket(order id: 1).')
        
    def test_remove_part(self):
        self.client.put('/service-tickets/1/add-part/1')
        response = self.client.put('/service-tickets/1/remove-part/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully removed one all-season tire from the ticket(order id: 1).')
    
    def test_add_service(self):
        response = self.client.put('/service-tickets/1/add-service/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully added Test Service to the ticket(order id: 1).')
    
    def test_remove_service(self):
        self.client.put('/service-tickets/1/add-service/1')
        response = self.client.put('/service-tickets/1/remove-service/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully removed Test Service from the ticket(order id: 1).')
    
    def test_receipt(self):
        self.client.put('/service-tickets/1/add-service/1')
        self.client.put('/service-tickets/1/add-part/1')
        response = self.client.get('/service-tickets/receipt/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_ticket_total'], 200)
        