from flask import Flask, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import customers_bp
from .schemas import customer_schema, customers_schema
from app.models import Customer, db

#create 
@customers_bp.route('/', methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    customer = db.session.execute(query).scalars().first()
    
    if customer:
        return jsonify({"error": "Email already associated with another account."}), 400
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201

#read
@customers_bp.route("/", methods=['GET'])
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(customers), 200

#get one customer
@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Invalid customer_id."}), 400

#update
@customers_bp.route("/<int:customer_id>", methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Invalid customer_id."}), 400
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    db_customer = db.session.execute(query).scalars().first()
    
    if db_customer and db_customer != customer:
        return jsonify({"error": "Email already associated with another account."}), 400
    
    for field, value in customer_data.items():
        setattr(customer, field, value)
        
    db.session.commit()
    return customer_schema.jsonify(customer), 200

#delete
@customers_bp.route("/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Invalid customer_id."}), 400
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {customer_id} was deleted."})