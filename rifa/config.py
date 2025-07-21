import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #DB_URL = os.getenv('DATABASE_URL')
    DB_URL = "postgresql://postgres:IzYxvHlBxYgfONoGNHcfkYFidxrajFXa@yamabiko.proxy.rlwy.net:51053/railway"
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret-key-default')
    PER_PAGE = 20
