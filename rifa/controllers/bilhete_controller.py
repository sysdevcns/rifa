from services.db_service import DatabaseService
from models.bilhete_model import BilheteModel

class BilheteController:
    @staticmethod
    def create(**kwargs):
        return BilheteModel.create(**kwargs)
    
    @staticmethod
    def search(numero=None, tipo=None, status=None, lote=None, data_inicio=None, data_fim=None):
        try:
            return BilheteModel.search(
                numero=numero,
                tipo=tipo,
                status=status,
                lote=lote,
                data_inicio=data_inicio,
                data_fim=data_fim
            )
        except Exception as e:
            raise Exception(f"Erro na busca de bilhetes: {str(e)}")
        
    @staticmethod
    def get_available(filters=None):
        """Obtém bilhetes disponíveis com filtros"""
        try:
            return BilheteModel.get_available(filters)
        except Exception as e:
            raise Exception(f"Erro ao buscar bilhetes disponíveis: {str(e)}")

    @staticmethod
    def get_stats():
        """Obtém estatísticas sobre bilhetes"""
        try:
            return BilheteModel.get_stats()
        except Exception as e:
            raise Exception(f"Erro ao obter estatísticas: {str(e)}")
        
    @staticmethod
    def get_stats_by_type():
        """Obtém estatísticas formatadas por tipo"""
        try:
            dados = BilheteModel.get_stats_by_type()
            
            if not dados:
                return {
                    'total': 0,
                    'por_tipo': {},
                    'detalhes': []
                }
                
            return {
                'total': sum(item['quantidade'] for item in dados),
                'por_tipo': {item['tipo']: item['quantidade'] for item in dados},
                'detalhes': dados
            }
        except Exception as e:
            raise Exception(f"Erro ao obter estatísticas por tipo: {str(e)}")
    

    @staticmethod
    def get_stats_by_lote():
        """Obtém estatísticas de bilhetes por lote"""
        try:
            conn = DatabaseService.get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COALESCE(lote, 'Sem Lote') as lote,
                        COUNT(*) as quantidade,
                        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Bilhetes)) as percentual
                    FROM Bilhetes
                    GROUP BY lote
                    ORDER BY quantidade DESC
                """)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao obter estatísticas por lote: {str(e)}")
        finally:
            conn.close()

    @staticmethod
    def get_full_report():
        """Obtém relatório completo de bilhetes"""
        try:
            conn = DatabaseService.get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id, numero, tipo, lote, status, 
                        observacoes, data_cadastro
                    FROM Bilhetes
                    ORDER BY data_cadastro DESC
                """)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao obter relatório completo: {str(e)}")
        finally:
            conn.close()