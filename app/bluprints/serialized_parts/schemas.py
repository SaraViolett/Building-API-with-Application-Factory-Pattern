from app.extensions import ma
from app.models import SerializedPart
from marshmallow import fields

class SerializedPartSchema(ma.SQLAlchemyAutoSchema):
    part_description = fields.Nested("PartDescriptionSchema")
    class Meta:
        model = SerializedPart
        include_fk = True
        
serialized_part_schema = SerializedPartSchema()
serialized_parts_schema = SerializedPartSchema(many=True)

view_serialized_part_schema = SerializedPartSchema(exclude=['part_id'])
view_serialized_parts_schema = SerializedPartSchema(exclude=['part_id'], many=True)
