
class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:leaRning1!@localhost/mechanics_shop_db'
    DEBUG = True
    
class TestingConfig:
    pass

class ProductionConfig:
    pass