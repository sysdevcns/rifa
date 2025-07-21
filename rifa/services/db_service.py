import psycopg
from urllib.parse import urlparse
from config import Config

class DatabaseService:
    @staticmethod
    def get_connection():
        try:
            url = urlparse(Config.DB_URL)
            conn = psycopg.connect(
                host=url.hostname,
                port=url.port,
                dbname=url.path[1:],
                user=url.username,
                password=url.password
            )
            return conn
        except Exception as e:
            raise Exception(f"Erro ao conectar ao banco de dados: {e}")

    @staticmethod
    def create_tables():
        # Implementação da criação de tabelas
        pass
