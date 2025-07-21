from services.db_service import DatabaseService
from controllers.bilhete_controller import BilheteController

class RelatorioModel:
    @staticmethod
    def generate_custom_report(filters):
        """Executa query complexa com base nos filtros"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                # Construir query dinâmica baseada nos filtros
                query = """
                    SELECT 
                        e.nome as evento_nome,
                        a.apelido as apostador_apelido,
                        j.numero as jogo_numero,
                        j.status as jogo_status,
                        p.valor as pagamento_valor,
                        p.metodo as pagamento_metodo
                    FROM Jogos j
                    LEFT JOIN Eventos e ON j.evento_id = e.id
                    LEFT JOIN Apostadores a ON j.apelido = a.apelido
                    LEFT JOIN Pagamentos p ON p.apelido = j.apelido
                    WHERE 1=1
                """
                
                params = []
                
                # Aplicar filtros dinamicamente
                if filters.get('start_date'):
                    query += " AND p.data >= %s"
                    params.append(filters['start_date'])
                
                # ... outros filtros
                
                cur.execute(query, params)
                return cur.fetchall()
        finally:
            conn.close()
            

    def generate_report_type():
        try:
            estatisticas =  BilheteController.get_stats_by_type()
            
            print("\nDistribuição por Tipo")
            print(f"Total de bilhetes: {estatisticas['total']}")
            print("\nQuantidade por tipo:")
            for tipo, quantidade in estatisticas['por_tipo'].items():
                print(f"- {tipo}: {quantidade}")
                
            return estatisticas
        except Exception as e:
            print(f"Erro ao gerar relatório: {str(e)}")
            return None