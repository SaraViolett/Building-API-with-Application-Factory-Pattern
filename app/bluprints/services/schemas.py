from app.models import Service
from app.extensions import ma

class ServiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service

service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)