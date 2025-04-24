from flask import jsonify, request
from . import service_tickets_bp
from .schemas import service_ticket_schema, service_tickets_schema
from app.models import db, ServiceTicket, Customer, Mechanic
from sqlalchemy import select, delete
from marshmallow import ValidationError
from app.bluprints.mechanics.schemas import mechanics_schema


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
        return service_ticket_schema.jsonify(new_ticket), 201
    return jsonify({"error": "Invalid customer id."})

#get tickets
@service_tickets_bp.route("/", methods=['GET'])
def get_service_tickets():
    query = select(ServiceTicket)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200

#get one ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=['GET'])
def get_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if ticket:
        return service_ticket_schema.jsonify(ticket), 200
    return jsonify({"error": "Invalid ticket_id."}), 400

#update ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=['PUT'])
def update_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Invalid ticket_id."}), 400
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in ticket_data.items():
        setattr(ticket, field, value)
        
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200

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
                "message": f"successfully added {mechanic.name} to the ticket.",
                "ticket": service_ticket_schema.dump(ticket),
                "mechanics": mechanics_schema.dump(ticket.mechanics)
            }), 200
        return jsonify({"error": f"{mechanic.name} already assigned to ticket"}),400
    return jsonify({"error": "invalid ticket_id or mechanic_id"}), 400

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
                "message": f"successfully removeded {mechanic.name} from the ticket.",
                "ticket": service_ticket_schema.dump(ticket),
                "mechanics": mechanics_schema.dump(ticket.mechanics)
            }), 200
        return jsonify({"error": f"{mechanic.name} not assigned to ticket"}), 400
    return jsonify({"error": "invalid mechanic_id or ticket_id"}), 400

#delete ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=['DELETE'])
def delete_service_ticket(ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message": f"succesfully deleted service_ticket {ticket_id}"})