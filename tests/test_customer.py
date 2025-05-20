from app import create_app
from app.models import db, Customer, ServiceTicket
import unittest
from app.utils.util import encode_token
from werkzeug.security import generate_password_hash
from datetime import datetime

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(
            name="Test", 
            email="test@email.com", 
            phone="123-123-test", 
            password=generate_password_hash("123")
            )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.ticket = ServiceTicket(
                VIN= "VIN12345",
                id= 1,
                customer_id= 1,
                service_date= datetime.strptime("2025-05-15", "%Y-%m-%d").date(),
                service_desc= "Replace Brakes"
            )
        with self.app.app_context():
            db.session.add(self.ticket)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()
        
    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
           	"phone": "123-123-test",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")
        
    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "123-123-test",
            "password": "123"       
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])
        
    def test_login_customer(self):
        credentials = {
            "email": "test@email.com",
            "password": "123"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(response.json['message'], 'Successfully Logged In')
        self.assertIn('token', response.json)
        
    def test_invalid_login_customer(self):
        payload = {
            "email": "testing@email.com",
            "password": "123",
        }
        response = self.client.post('/customers/login', json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['messages'], 'Invalid email or password')
        
    def test_customer_update(self):
        update_payload = {
            "name": "New customer",
            "email": "tester@email.com",
            "phone": "123",
            "password": generate_password_hash("123")
        }
        headers = {"Authorization": "Bearer "+ self.token}
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'New customer')
        
    def test_get_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test')
        
    def test_get_single_customer(self):
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test')
        
    def test_invalid_get_single_customer(self):
        response = self.client.get('/customers/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid customer_id.')
        
    def test_customer_delete(self):
        headers = {"Authorization": "Bearer "+ self.token}
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Customer Test was deleted.')
        
    def test_search_customers(self):
        response = self.client.get('/customers/search?search=Test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['customers'][0]['name'], 'Test')
        
    def test_paginated_customers(self):
        response = self.client.get('/customers/paginated?page=1&per_page=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test')
        
    def test_customer_tickets(self):
        headers = {"Authorization": "Bearer "+ self.token}
        response = self.client.get('/customers/my-tickets', headers=headers)
        print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['tickets'][0]['id'], 1)
