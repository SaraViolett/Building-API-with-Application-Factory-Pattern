import unittest
from app import create_app

from app.models import db, Mechanic
from app.utils.util import encode_token
from werkzeug.security import generate_password_hash

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(
            name="Test",
            email="test@email.com",
            phone="123",
            salary=1,
            password=generate_password_hash("123")
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()
        
    def test_login_mechanic(self):
        payload = {
            "email": "test@email.com",
            "password": "123",
        }
        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)
        
    def test_invalid_login_mechanic(self):
        payload = {
            "email": "testing@email.com",
            "password": "123",
        }
        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['messages'], 'Invalid email or password')
        
    def test_mechanic_update(self):
        update_payload = {
            "name": "New Mechanic",
            "email": "test@email.com",
            "phone": "123",
            "salary": 100000,
            "password": generate_password_hash("123")
        }
        headers = {"Authorization": "Bearer "+ self.token}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'New Mechanic')
        
    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "New Mechanic",
            "email": "testing@email.com",
           	"phone": "123-123-test",
            "salary": 10000,
            "password": generate_password_hash("123")
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "New Mechanic")
        
    def test_invalid_creation(self):
        mechanic_payload = {
            "name": "New Mechanic",
            "phone": "123-123-test",
            "salary": 10000,
            "password": generate_password_hash("123")      
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])
        
    def test_get_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test')
        
    def test_get_single_mechanic(self):
        response = self.client.get('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test')
        
    def test_invalid_get_single_mechanic(self):
        response = self.client.get('/mechanics/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid mechanic_id.')
        
    def test_mechanic_delete(self):
        headers = {"Authorization": "Bearer "+ self.token}
        response = self.client.delete('/mechanics/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Mechanic Test was deleted.')
        
    def test_mechanic_activity_tracker(self):
        response = self.client.get('/mechanics/activity-tracker')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'success')
        
    def test_search_mechanics(self):
        response = self.client.get('/mechanics/search?search=test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['mechanics'][0]['name'], 'Test')
        
    def test_paginated_mechanics(self):
        response = self.client.get('/mechanics/paginated?page=1&per_page=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test')
