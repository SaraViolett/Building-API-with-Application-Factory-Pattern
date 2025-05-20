from flask import Flask, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import part_descriptions_bp
from app.bluprints.part_descriptions.schemas import part_schema, parts_schema
from app.models import PartDescription, db
from app.extensions import limiter


#create part
@part_descriptions_bp.route('/', methods=['POST'])
def create_part():
    try:
        part_description_data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_part = PartDescription(**part_description_data)
    db.session.add(new_part)
    db.session.commit()
    
    return part_schema.jsonify(new_part), 201

#read/Get parts
@part_descriptions_bp.route("/", methods=['GET'])
@limiter.exempt #this is likely a frequently used operation during the day in the shop that you wouldn't want to limit because that could impact business
def get_parts():
    query = select(PartDescription)
    parts = db.session.execute(query).scalars().all()
    return parts_schema.jsonify(parts), 200

#get one part
@part_descriptions_bp.route("/<int:part_id>", methods=['GET'])
def get_part(part_id):
    part = db.session.get(PartDescription, part_id)
    if part:
        return part_schema.jsonify(part), 200
    return jsonify({"error": "Invalid part_description_id."}), 400


#update
@part_descriptions_bp.route("/<int:part_id>", methods=['PUT'])
@limiter.limit("25 per hour") #probably wouldn't update parts frequently.
def update_part(part_id):
    part = db.session.get(PartDescription, part_id)
    if not part:
        return jsonify({"error": "Invalid part_id."}), 400
    try:
        part_description_data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in part_description_data.items():
        setattr(part, field, value)
        
    db.session.commit()
    return part_schema.jsonify(part), 200

#delete
@part_descriptions_bp.route("/<int:part_id>", methods=['DELETE'])
@limiter.limit("5 per hour") #probably wouldn't delete(fire) parts frequently. Assumption is that this is a small shop with < 15 employees
def delete_part(part_id):
    part = db.session.get(PartDescription, part_id)
    
    if not part:
        return jsonify({"error": "Invalid part_id."}), 400
    
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Part {part.id} was deleted."})
    
    

