from flask import jsonify, request
from . import service_tickets_bp
from .schemas import service_ticket_schema, update_service_ticket_schema, view_service_ticket_schema, view_service_tickets_schema, service_ticket_receipt_schema, service_ticket_response_schema
from app.models import db, ServiceTicket, Customer, Mechanic, PartDescription, Service
from sqlalchemy import select, delete
from marshmallow import ValidationError
from app.extensions import cache


#create tickets
@service_tickets_bp.route("/", methods=["POST"])
def create_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer = db.session.query(Customer, ticket_data['customer_id'])
    if customer:
        new_ticket = ServiceTicket(**ticket_data)
        db.session.add(new_ticket)
        db.session.commit()
        return service_ticket_response_schema.jsonify(new_ticket), 201
    return jsonify({"error": "Invalid customer id."})

#get tickets
@service_tickets_bp.route("/", methods=['GET'])
@cache.cached(timeout=60) #this end point might be used frequently so caching could improve performance
def get_service_tickets():
    query = select(ServiceTicket)
    result = db.session.execute(query).scalars().all()
    return view_service_tickets_schema.jsonify(result), 200

#get one ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=['GET'])
def get_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if ticket:
        return view_service_ticket_schema.jsonify(ticket), 200
    return jsonify({"error": "Invalid ticket_id."}), 400

#get ticket receipt with total cost
@service_tickets_bp.route("/receipt/<int:ticket_id>", methods=['GET'])
def get_ticket_receipt(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if ticket:
        
        parts_total = 0
        for part in ticket.serialized_parts:
            parts_total += part.part_description.price
            
        service_labor_total = 0
        for service in ticket.services:
            service_labor_total = service.labor_hours * service.labor_rate
        
        service_ticket_total = parts_total + service_labor_total
        
        receipt = {
            "service_ticket": ticket,
            "parts_total": parts_total,
            "service_labor_total": service_labor_total,
            "service_ticket_total": service_ticket_total
        }
        return service_ticket_receipt_schema.jsonify(receipt), 200
    return jsonify({"error": "Invalid ticket_id."}), 400

#update ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=['PUT'])
def update_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Invalid ticket_id."}), 400
    try:
        ticket_data = update_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in ticket_data.items():
        setattr(ticket, field, value)
        
    db.session.commit()
    return service_ticket_response_schema.jsonify(ticket), 200

#add mechanic to ticket
@service_tickets_bp.route("/<int:ticket_id>/add-mechanic/<int:mechanic_id>", methods=['PUT'])
def add_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if ticket and mechanic:
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
            db.session.commit()
            return jsonify({
                "message": f"Successfully added {mechanic.name} to the ticket(order id: {ticket.id}).",
                "ticket": view_service_ticket_schema.dump(ticket),
            }), 200
        return jsonify({"error": f"{mechanic.name} already assigned to this ticket."}),400
    return jsonify({"error": "Invalid ticket_id or mechanic_id"}), 400

#remove mechanic from ticket
@service_tickets_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if ticket and mechanic:
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
            db.session.commit()
            return jsonify({
                "message": f"Successfully removed {mechanic.name} from the ticket(order id: {ticket.id}).",
                "ticket": view_service_ticket_schema.dump(ticket)
            }), 200
        return jsonify({"error": f"{mechanic.name} not assigned to ticket"}), 400
    return jsonify({"error": "invalid mechanic_id or ticket_id"}), 400

#add part to ticket
@service_tickets_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=['PUT'])
def add_part(ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(PartDescription, part_id)
    
    if ticket and part:
        for serialized_part in part.serialized_parts:
            if serialized_part.ticket_id == None:
                ticket.serialized_parts.append(serialized_part)
                db.session.commit()
                return jsonify({
                        "message": f"Successfully added one {part.part_name} to the ticket(order id: {ticket.id}).",
                        "ticket": view_service_ticket_schema.dump(ticket),
                    }), 200
        return jsonify({"error": f"{part.part_name} out of stock."}),400
    return jsonify({"error": "Invalid ticket_id or part_id"}), 400

#remove single part from ticket by id 
@service_tickets_bp.route("/<int:ticket_id>/remove-part/<int:part_id>", methods=['PUT'])
def remove_part(ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(PartDescription, part_id)
    
    if ticket and part:
        for serialized_part in ticket.serialized_parts:
            print("serialized_part.part.id:", serialized_part.part_id,
                  "serialized_part.part_description.id:", serialized_part.part_description.id)
            if serialized_part.part_id == part.id:
                ticket.serialized_parts.remove(serialized_part)
                db.session.commit()
                return jsonify({
                        "message": f"Successfully removed one {part.part_name} from the ticket(order id: {ticket.id}).",
                        "ticket": view_service_ticket_schema.dump(ticket),
                    }), 200
        return jsonify({"error": f"{part.part_name} not associated with this ticket."}),400
    return jsonify({"error": "Invalid ticket_id or part_id"}), 400

#add service to ticket
@service_tickets_bp.route("/<int:ticket_id>/add-service/<int:service_id>", methods=['PUT'])
def add_service(ticket_id, service_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    service = db.session.get(Service, service_id)
    
    if ticket and service:
        if service not in ticket.services:
            ticket.services.append(service)
            db.session.commit()
            return jsonify({
                "message": f"Successfully added {service.name} to the ticket(order id: {ticket.id}).",
                "ticket": view_service_ticket_schema.dump(ticket),
            }), 200
        return jsonify({"error": f"{service.name} already assigned to this ticket."}),400
    return jsonify({"error": "Invalid ticket_id or service_id"}), 400

#remove service from ticket
@service_tickets_bp.route("/<int:ticket_id>/remove-service/<int:service_id>", methods=['PUT'])
def remove_service(ticket_id, service_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    service = db.session.get(Service, service_id)
    
    if ticket and service:
        if service in ticket.services:
            ticket.services.remove(service)
            db.session.commit()
            return jsonify({
                "message": f"Successfully removed {service.name} from the ticket(order id: {ticket.id}).",
                "ticket": view_service_ticket_schema.dump(ticket)
            }), 200
        return jsonify({"error": f"{service.name} not assigned to ticket"}), 400
    return jsonify({"error": "invalid service_id or ticket_id"}), 400

#delete ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=['DELETE'])
def delete_service_ticket(ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    if service_ticket: 
        db.session.delete(service_ticket)
        db.session.commit()
        return jsonify({"message": f"Succesfully deleted service Ticket {ticket_id}"})
    return jsonify({"error": "invalid ticket_id"}), 400