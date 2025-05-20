import unittest
from app import create_app

from app.models import db, Service

class TestService(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.service = Service(
            name="Test",
            labor_hours= 1,
           	labor_rate= 100
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.service)
            db.session.commit()
        self.client = self.app.test_client()
        
    def test_create_service(self):
        service_payload = {
            "name": "New service",
            "labor_hours": 1,
           	"labor_rate": 100
        }

        response = self.client.post('/services/', json=service_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], "Successfully created new service")
        
    def test_invalid_creation(self):
        service_payload = {
            "name": "New service",
            "labor_rate": 100,      
        }

        response = self.client.post('/services/', json=service_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['labor_hours'], ['Missing data for required field.'])
        
    def test_service_update(self):
        update_payload = {
            "name": "New service",
            "labor_hours": 1.5,
           	"labor_rate": 100
        }
        response = self.client.put('/services/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'New service')
        
    def test_get_services(self):
        response = self.client.get('/services/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test')
        
    def test_get_single_service(self):
        response = self.client.get('/services/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test')
        
    def test_invalid_get_single_service(self):
        response = self.client.get('/services/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid service_id')
        
    def test_service_delete(self):
        response = self.client.delete('/services/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Test was deleted.')
        
    def test_invalid_service_delete(self):
        response = self.client.delete('/services/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid service_id')

