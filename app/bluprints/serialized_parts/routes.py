from flask import Flask, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import serialized_parts_bp
from .schemas import serialized_part_schema, serialized_parts_schema, view_serialized_part_schema, view_serialized_parts_schema
from app.models import SerializedPart, db
from app.extensions import limiter


#create part
@serialized_parts_bp.route('/', methods=['POST'])
def create_part():
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
   
    new_serialized_part = SerializedPart(**serialized_part_data)
    db.session.add(new_serialized_part)
    db.session.commit()
    
    return serialized_part_schema.jsonify(new_serialized_part), 201

#read/Get parts
@serialized_parts_bp.route("/", methods=['GET'])
@limiter.exempt #this is likely a frequently used operation during the day in the shop that you wouldn't want to limit because that could impact business
def get_parts():
    query = select(SerializedPart)
    parts = db.session.execute(query).scalars().all()
    return serialized_parts_schema.jsonify(parts), 200

#read/Get parts paginated
@serialized_parts_bp.route("/paginated", methods=['GET'])
@limiter.exempt #this is likely a frequently used operation during the day in the shop that you wouldn't want to limit because that could impact business
def get_parts_paginated():
    page = int(request.args.get("page"))
    per_page = int(request.args.get("per_page"))
    
    query = select(SerializedPart)
    parts = db.paginate(query, page=page, per_page=per_page)
    return serialized_parts_schema.jsonify(parts)

#get one part
@serialized_parts_bp.route("/<int:part_id>", methods=['GET'])
def get_part(part_id):
    part = db.session.get(SerializedPart, part_id)
    if part:
        return serialized_part_schema.jsonify(part), 200
    return jsonify({"error": "Invalid mechaninc_id."}), 400

#query parameter endpoint- search by part name
@serialized_parts_bp.route("/search", methods=["GET"])
def search_part():
    name = request.args.get('search')
    query = select(SerializedPart).where(SerializedPart.part_name.ilike(f"%{name}%"))
    parts = db.session.execute(query).scalars().all()
    
    return jsonify({"parts": view_serialized_parts_schema.dump(parts)})

#update
@serialized_parts_bp.route("/<int:part_id>", methods=['PUT'])
@limiter.limit("25 per hour") #probably wouldn't update parts frequently.
def update_part(part_id):
    part = db.session.get(SerializedPart, part_id)
    if not part:
        return jsonify({"error": "Invalid part_id."}), 400
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in serialized_part_data.items():
        setattr(part, field, value)
        
    db.session.commit()
    return view_serialized_part_schema.jsonify(part), 200

#delete
@serialized_parts_bp.route("/<int:part_id>", methods=['DELETE'])
@limiter.limit("5 per hour") #probably wouldn't delete(fire) parts frequently. Assumption is that this is a small shop with < 15 employees
def delete_part(part_id):
    part = db.session.get(SerializedPart, part_id)
    
    if not part:
        return jsonify({"error": "Invalid part_id."}), 400
    
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Part {part.id} was deleted."})
