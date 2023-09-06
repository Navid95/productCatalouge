from app import ENV

if ENV == 'DEVELOP':
    SQLALCHEMY_DATABASE_URI = 'sqlite:///develop.db'
