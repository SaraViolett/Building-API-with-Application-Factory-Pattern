from flask import Flask, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import customers_bp
from .schemas import customer_schema, login_schema, view_customers_schema
from app.models import Customer, db
from app.extensions import limiter
from app.utils.util import encode_token, token_required
from app.bluprints.service_tickets.schemas import service_tickets_customer_schema
from werkzeug.security import generate_password_hash, check_password_hash

#customer login
@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query =select(Customer).where(Customer.email == credentials['email']) 
    customer = db.session.execute(query).scalars().first() #Query customers table for a customer with this email

    if customer and check_password_hash(customer.password, credentials['password']): #if we have a customer associated with the username, validate the password
        token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "token": token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401

#create customer
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
    
    hashed_password = generate_password_hash(customer_data['password'])
    customer_data['password'] = hashed_password  
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201

#read/get
@customers_bp.route("/", methods=['GET'])
@limiter.exempt #this could be a frequent call in normal business operations that you wouldn't want to limit
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    return view_customers_schema.jsonify(customers), 200

#read/get customers paginated
@customers_bp.route("/paginated", methods=['GET'])
@limiter.exempt #this is likely a frequently used operation during the day in the shop that you wouldn't want to limit because that could impact business
def get_customers_paginated():
    page = int(request.args.get("page"))
    per_page = int(request.args.get("per_page"))
    
    query = select(Customer)
    customers = db.paginate(query, page=page, per_page=per_page)
    return view_customers_schema.jsonify(customers)

#query parameter endpoint- search by customer name
@customers_bp.route("/search", methods=["GET"])
def search_customer():
    name = request.args.get('search')
    query = select(Customer).where(Customer.name.ilike(f"%{name}%"))
    customers = db.session.execute(query).scalars().all()
    
    return jsonify({"customers": view_customers_schema.dump(customers)})
    

#get one customer
@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Invalid customer_id."}), 400

#get tickets for one customer with token
@customers_bp.route("/my-tickets", methods=['GET'])
@token_required
def get_customer_tickets():
    customer_id = getattr(request, 'id', None) 
    if not customer_id:
        return jsonify({"error": "Customer ID not found in request"}), 400

    customer = db.session.get(Customer, customer_id)
    if customer:
        if customer.tickets:
            return jsonify({"tickets": service_tickets_customer_schema.dump(customer.tickets)}), 200
        return jsonify({"error": "You have no service tickets"}), 200
    return jsonify({"error": "Invalid customer ID"}), 400

#update
@customers_bp.route("/", methods=['PUT'])
@token_required
@limiter.limit("20/hour") #since this is a small shop, there wouldn't be that many changes to customers per hour
def update_customer():
    customer = db.session.get(Customer, request.id)
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
    
    hashed_password = generate_password_hash(customer_data['password'])
    customer_data['password'] = hashed_password 
    
    for field, value in customer_data.items():
        setattr(customer, field, value)
        
    db.session.commit()
    return customer_schema.jsonify(customer), 200

#delete
@customers_bp.route("/", methods=['DELETE'])
@token_required
@limiter.limit("3 per hour") #probably wouldn't delete that many customers since this is a small shop
def delete_customer():
    customer = db.session.get(Customer, request.id)
    
    if not customer:
        return jsonify({"error": "Invalid customer_id."}), 400
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {customer.name} was deleted."}), 200