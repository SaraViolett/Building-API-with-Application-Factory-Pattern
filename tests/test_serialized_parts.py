import unittest
from app import create_app

from app.models import db, SerializedPart, PartDescription

class TestSerializedPart(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.part = SerializedPart(
            part_id=1,
            ticket_id=None,
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.part)
            db.session.commit()
        self.part_description_1 = PartDescription(
                part_name= "all-seaon tire",
                id= 1,
                price= 100,
                brand= "Best Tires"
            )
        with self.app.app_context():
            db.session.add(self.part_description_1)
            db.session.commit()
        self.part_description_2 = PartDescription(
                part_name= "snow tire",
                id= 2,
                price= 120,
                brand= "Best Tires"
            )
        with self.app.app_context():
            db.session.add(self.part_description_2)
            db.session.commit()
        self.client = self.app.test_client()
        
    def test_create_part(self):
        part_payload = {
            "part_id": 1
        }

        response = self.client.post('/serialized-parts/', json=part_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_description']['part_name'], 'all-seaon tire')
        
    def test_invalid_creation(self):
        part_payload = {
                  
        }

        response = self.client.post('/serialized-parts/', json=part_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['part_id'], ['Missing data for required field.'])
        
    def test_part_update(self):
        update_payload = {
            "part_id": 2
        }
        response = self.client.put('/serialized-parts/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_description']['part_name'], 'snow tire')
        
    def test_get_parts(self):
        response = self.client.get('/serialized-parts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['part_description']['part_name'], 'all-seaon tire')
        
    def test_get_single_part(self):
        response = self.client.get('/serialized-parts/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_description']['part_name'], 'all-seaon tire')
        
    def test_invalid_get_single_part(self):
        response = self.client.get('/serialized-parts/3')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid serialized_part_id.')
        
    def test_part_delete(self):
        response = self.client.delete('/serialized-parts/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Serialized part 1 was deleted.')
        
    def test_invalid_part_delete(self):
        response = self.client.delete('/serialized-parts/2')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid serialized_part_id.')

