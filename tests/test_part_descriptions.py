import unittest
from app import create_app

from app.models import db, PartDescription

class TestPartDescription(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.part_description = PartDescription(
            part_name="Test",
            brand= "Tester",
           	price= 100
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.part_description)
            db.session.commit()
        self.client = self.app.test_client()
        
    def test_create_part_description(self):
        part_description_payload = {
            "part_name": "New part",
            "brand": "Pro Parts",
           	"price": 100
        }

        response = self.client.post('/part-descriptions/', json=part_description_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], "New part")
        
    def test_invalid_creation(self):
        part_description_payload = {
            "part_name": "New part",
            "brand": "Pro Parts",      
        }

        response = self.client.post('/part-descriptions/', json=part_description_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['price'], ['Missing data for required field.'])
        
    def test_part_description_update(self):
        update_payload = {
            "part_name": "New part",
            "brand": "Tester",
           	"price": 100
        }
        response = self.client.put('/part-descriptions/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'New part')
        
    def test_get_part_descriptions(self):
        response = self.client.get('/part-descriptions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['part_name'], 'Test')
        
    def test_get_single_part_description(self):
        response = self.client.get('/part-descriptions/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'Test')
        
    def test_invalid_get_single_part_description(self):
        response = self.client.get('/part-descriptions/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid part_description_id.')
        
    def test_part_description_delete(self):
        response = self.client.delete('/part-descriptions/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Part 1 was deleted.')
        
    def test_invalid_part_description_delete(self):
        response = self.client.delete('/part-descriptions/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid part_id.')

