from app.extensions import ma
from app.models import Customer
from marshmallow import fields

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

login_schema = CustomerSchema(exclude=['name','phone'])

view_customers_schema = CustomerSchema(exclude=['password'], many=True)