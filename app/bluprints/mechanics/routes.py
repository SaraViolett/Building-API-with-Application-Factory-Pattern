from flask import Flask, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema
from app.models import Mechanic, db

#create 
@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic:
        return jsonify({"error": "Email already associated with another account."}), 400
    
    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    
    return mechanic_schema.jsonify(new_mechanic), 201

#read
@mechanics_bp.route("/", methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200

#get one mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Invalid mechaninc_id."}), 400

#update
@mechanics_bp.route("/<int:mechanic_id>", methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Invalid mechanic_id."}), 400
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    db_mechanic = db.session.execute(query).scalars().first()
    
    if db_mechanic and db_mechanic != mechanic:
        return jsonify({"error": "Email already associated with another account."}), 400
    
    for field, value in mechanic_data.items():
        setattr(mechanic, field, value)
        
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

#delete
@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic:
        return jsonify({"error": "Invalid mechanic_id."}), 400
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {mechanic_id} was deleted."})