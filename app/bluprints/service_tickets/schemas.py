from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested("MechanicSchema", exclude=['password', 'salary'], many=True)
    customer = fields.Nested("CustomerSchema", exclude=['password'])
    serialized_parts = fields.Nested("SerializedPartSchema", exclude=['part_id', 'ticket_id'], many=True)
    services = fields.Nested("ServiceSchema", many=True)
    class Meta:
        model = ServiceTicket
        include_fk=True
class ServiceTicketReceiptSchema(ma.Schema):
    service_ticket = fields.Nested("ServiceTicketSchema", exclude=['customer_id'])
    parts_total = fields.Int(required=True)
    service_labor_total = fields.Int(required=True)
    service_ticket_total = fields.Int(required=True)


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

update_service_ticket_schema = ServiceTicketSchema(exclude=['id'])

view_service_ticket_schema = ServiceTicketSchema(exclude=['customer_id'])
view_service_tickets_schema = ServiceTicketSchema(exclude=['customer_id'], many=True)

service_ticket_receipt_schema = ServiceTicketReceiptSchema()