import os

class Config(object):
  SQLALCHEMY_DATABASE_URI = os.environ['DB_URL'] 
