from flask import Flask, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanics_bp
from app.bluprints.mechanics.schemas import mechanic_schema, login_schema, view_mechanic_schema, view_mechanics_schema, mechanic_activity_schema
from app.models import Mechanic, db
from app.extensions import limiter
from app.utils.util import encode_token, token_required
from werkzeug.security import generate_password_hash, check_password_hash

@mechanics_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query =select(Mechanic).where(Mechanic.email == credentials['email']) 
    mechanic = db.session.execute(query).scalars().first() #Query mechanic table for a mechanic with this email

    if mechanic and check_password_hash(mechanic.password, credentials['password']): #if we have a mechanic associated with the username, validate the password
        token = encode_token(mechanic.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "token": token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401


#create 
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("15 per hour") #probably wouldn't create many mechanics,  this is with the assumption that this is a small shop with < 15 employees
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic:
        return jsonify({"error": "Email already associated with another account."}), 400
    
    hashed_password = generate_password_hash(mechanic_data['password'])
    mechanic_data['password'] = hashed_password 
    
    
    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    
    return mechanic_schema.jsonify(new_mechanic), 201

#Read/Get all mechanics
@mechanics_bp.route("/", methods=['GET'])
@limiter.exempt #this is likely a frequently used operation during the day in the shop that you wouldn't want to limit because that could impact business
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    return view_mechanics_schema.jsonify(mechanics), 200

#get one mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if mechanic:
        return view_mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Invalid mechanic_id."}), 400

#update
@mechanics_bp.route("/", methods=['PUT'])
@limiter.limit("15 per hour") #probably wouldn't update mechanics frequently, maybe once a year they each get a small raise. Assumption is that this is a small shop with < 15 employees
@token_required
def update_mechanic():
    mechanic = db.session.get(Mechanic, request.id)
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
    
    hashed_password = generate_password_hash(mechanic_data['password'])
    mechanic_data['password'] = hashed_password 
    
    for field, value in mechanic_data.items():
        setattr(mechanic, field, value)
        
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

#delete
@mechanics_bp.route("/", methods=['DELETE'])
@limiter.limit("5 per hour") #probably wouldn't delete(fire) mechanics frequently. Assumption is that this is a small shop with < 15 employees
@token_required
def delete_mechanic():
    mechanic = db.session.get(Mechanic, request.id)
    
    if not mechanic:
        return jsonify({"error": "Invalid mechanic id."}), 400
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {mechanic.name} was deleted."}), 200

#query mechanics with most tickets
@mechanics_bp.route("/activity-tracker", methods=["GET"])
def get_mechanics_activity():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
    mechanics.sort(key=lambda mechanic: len(mechanic.tickets))
    return jsonify({"message": "success",
                    "mechanics": mechanic_activity_schema.dump(mechanics[::-1])}), 200
    
#query parameter endpoint- search by mechanic name
@mechanics_bp.route("/search", methods=["GET"])
def search_mechanic():
    name = request.args.get('search')
    query = select(Mechanic).where(Mechanic.name.ilike(f"%{name}%"))
    mechanics = db.session.execute(query).scalars().all()
    
    return jsonify({"mechanics": view_mechanics_schema.dump(mechanics)}), 200
    
#read/Get mechanics paginated
@mechanics_bp.route("/paginated", methods=['GET'])
@limiter.exempt #this is likely a frequently used operation during the day in the shop that you wouldn't want to limit because that could impact business
def get_mechanics_paginated():
    page = int(request.args.get("page"))
    per_page = int(request.args.get("per_page"))
    
    query = select(Mechanic)
    mechanics = db.paginate(query, page=page, per_page=per_page)
    return view_mechanics_schema.jsonify(mechanics), 200 
