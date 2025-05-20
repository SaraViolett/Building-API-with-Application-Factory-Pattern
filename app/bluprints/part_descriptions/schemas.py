from app.extensions import ma
from app.models import PartDescription

class PartDescriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartDescription
part_schema = PartDescriptionSchema()
parts_schema = PartDescriptionSchema(many=True)