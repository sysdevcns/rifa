from services.db_service import DatabaseService
from models.fixo_model import FixoModel

class FixoController:
    @staticmethod
    def create(apelido, numero, grupo=None, status="Ativo"):
        return FixoModel.create(
            apelido=apelido,
            numero=numero,
            grupo=grupo,
            status=status
        )
    
    @staticmethod
    def update(fixo_id, **kwargs):
        """Atualiza um jogo fixo"""
        try:
            return FixoModel.update(fixo_id, **kwargs)
        except Exception as e:
            raise Exception(f"Erro ao atualizar jogo fixo: {str(e)}")

    @staticmethod
    def search(apelido=None, status=None, grupo=None, numero=None):
        """Busca jogos fixos com filtros"""
        try:
            return FixoModel.search(
                apelido=apelido,
                status=status,
                grupo=grupo,
                numero=numero
            )
        except Exception as e:
            raise Exception(f"Erro ao buscar jogos fixos: {str(e)}")

    @staticmethod
    def apply_to_event(evento_id, apelido=None, grupo=None):
        """Aplica jogos fixos a um evento específico"""
        try:
            return FixoModel.apply_to_event(
                evento_id=evento_id,
                apelido=apelido,
                grupo=grupo
            )
        except Exception as e:
            raise Exception(f"Erro ao aplicar jogos ao evento: {str(e)}")
        
    @staticmethod
    def count_active():
        """Conta jogos fixos ativos"""
        try:
            conn = DatabaseService.get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM Fixos 
                    WHERE status = 'Ativo'
                """)
                return cur.fetchone()[0]
        except Exception as e:
            raise Exception(f"Erro ao contar jogos fixos ativos: {str(e)}")
        finally:
            conn.close()        
            
    @staticmethod
    def get_all():
        """Obtém todos os jogos fixos"""
        try:
            return FixoModel.search()  # Usa o método search sem filtros para obter todos
        except Exception as e:
            raise Exception(f"Erro ao buscar todos os jogos fixos: {str(e)}")
    
    @staticmethod
    def get_all_active():
        """Obtém todos os jogos fixos ativos"""
        try:
            return FixoModel.get_all_active()
        except Exception as e:
            raise Exception(f"Erro ao buscar jogos fixos ativos: {str(e)}")
        
    @staticmethod
    def get_by_id(fixo_id):
        """Obtém um jogo fixo pelo ID"""
        try:
            return FixoModel.get_by_id(fixo_id)
        except Exception as e:
            raise Exception(f"Erro ao buscar jogo fixo por ID: {str(e)}")
            
    @staticmethod
    def batch_update_status(apelido=None, grupo=None, status='Ativo'):
        """Atualiza status em lote para jogos fixos"""
        try:
            return FixoModel.batch_update_status(apelido, grupo, status)
        except Exception as e:
            raise Exception(f"Erro ao atualizar status em lote: {str(e)}")