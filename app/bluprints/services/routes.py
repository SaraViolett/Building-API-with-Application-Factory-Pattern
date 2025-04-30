from flask import Flask, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import services_bp
from .schemas import service_schema, services_schema
from app.models import Service, db

#Create Service
@services_bp.route("/", methods=['POST'])
def create_service():
    try:
        service_data = service_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_service = Service(**service_data)
    db.session.add(new_service)
    db.session.commit()
    return jsonify({"status": "success",
                    "message": "Successfully created new service",
                    "new_service": service_schema.dump(new_service)}), 201
    
#read/get all services
@services_bp.route("/", methods=['GET'])
def get_services():
    query = select(Service)
    services = db.session.execute(query).scalars().all()
    return services_schema.jsonify(services), 200

#read/get single service by id
@services_bp.route("/<int:service_id>", methods=['GET'])
def get_service(service_id):
    service = db.session.get(Service, service_id)
    if service:
        return service_schema.jsonify(service), 200
    return jsonify({"error": "Invalid service_id"}), 400

#update service
@services_bp.route("/<int:service_id>", methods=['PUT'])
def update_service(service_id):
    service = db.session.get(Service, service_id)
    if not service:
        return jsonify({"error":"Invalid service_id"})
    try: 
        service_data = service_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in service_data.items():
        setattr(service, field, value)
        
    db.session.commit()
    return service_schema.jsonify(service), 200

#delete service
@services_bp.route("/<int:service_id>", methods=['DELETE'])
def delete_service(service_id):
    service = db.session.get(Service, service_id)
    if not service:
        return jsonify({"error":"Invalid service_id"}), 400
    db.session.delete(service)
    db.session.commit()
    return jsonify({"message": f"{service.name} was deleted."}), 200

