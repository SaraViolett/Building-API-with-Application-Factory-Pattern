from flask import Flask
from app.extensions import ma, limiter, cache
from app.models import db
from app.bluprints.customers import customers_bp
from app.bluprints.mechanics import mechanics_bp
from app.bluprints.service_tickets import service_tickets_bp
from app.bluprints.part_descriptions import part_descriptions_bp
from app.bluprints.serialized_parts import serialized_parts_bp
from app.bluprints.services import services_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'  

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "MachanicShopAPI"
    }
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    #initialize extensions
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    #register blueprints
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(services_bp, url_prefix="/services")
    app.register_blueprint(service_tickets_bp, url_prefix="/service-tickets")
    app.register_blueprint(part_descriptions_bp, url_prefix="/part-descriptions")
    app.register_blueprint(serialized_parts_bp, url_prefix="/serialized-parts")
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL) 
    
    return app
