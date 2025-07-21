from services.db_service import DatabaseService
from models.pagamento_model import PagamentoModel

class PagamentoController:
    @staticmethod
    def create(numero, apelido, valor, metodo, observacoes, jogos):
        """Registra um novo pagamento e marca os jogos como vendidos"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                # 1. Verifica se os jogos ainda estão reservados
                for num in jogos:
                    cur.execute(
                        """SELECT status FROM Jogos 
                        WHERE numero = %s AND apelido = %s""",
                        (num, apelido)
                    )
                    result = cur.fetchone()
                    if not result or result[0] != 'RESERVADO':
                        raise ValueError(f"Jogo {num} não está mais disponível para pagamento")
                
                # 2. Insere o pagamento
                cur.execute(
                    """INSERT INTO Pagamentos 
                    (numero, apelido, valor, metodo, observacoes)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id""",
                    (numero, apelido, valor, metodo, observacoes)
                )
                pagamento_id = cur.fetchone()[0]
                
                # 3. Atualiza o status dos jogos
                for num in jogos:
                    cur.execute(
                        """UPDATE Jogos 
                        SET status = 'VENDIDO', 
                            data_venda = CURRENT_TIMESTAMP
                        WHERE numero = %s AND apelido = %s""",
                        (num, apelido)
                    )
                
                conn.commit()
                return pagamento_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao registrar pagamento: {str(e)}")
        finally:
            conn.close()

    @staticmethod
    def search(apelido=None, status=None, metodo=None, data_inicio=None, data_fim=None):
        """Busca pagamentos com filtros"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = """SELECT p.id, p.numero, p.apelido, a.Nome as nome_apostador,
                          p.valor, p.metodo, p.status, p.data_registro as data,
                          p.observacoes
                          FROM Pagamentos p
                          JOIN Apostadores a ON p.apelido = a.Apelido
                          WHERE 1=1"""
                params = []
                
                if apelido:
                    query += " AND p.apelido = %s"
                    params.append(apelido)
                
                if status:
                    query += " AND p.status = %s"
                    params.append(status)
                
                if metodo:
                    query += " AND p.metodo = %s"
                    params.append(metodo)
                
                if data_inicio:
                    query += " AND p.data_registro >= %s"
                    params.append(data_inicio)
                
                if data_fim:
                    query += " AND p.data_registro <= %s"
                    params.append(data_fim)
                
                query += " ORDER BY p.data_registro DESC"
                
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao buscar pagamentos: {str(e)}")
        finally:
            conn.close()

    @staticmethod
    def update_status(pagamento_id, novo_status):
        """Atualiza o status de um pagamento"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE Pagamentos 
                    SET status = %s 
                    WHERE id = %s""",
                    (novo_status, pagamento_id)
                )
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao atualizar status: {str(e)}")
        finally:
            conn.close()

    @staticmethod
    def get_by_id(pagamento_id):
        """Obtém um pagamento pelo ID"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT p.id, p.numero, p.apelido, a.Nome as nome_apostador,
                       p.valor, p.metodo, p.status, p.data_registro, p.observacoes
                       FROM Pagamentos p
                       JOIN Apostadores a ON p.apelido = a.Apelido
                       WHERE p.id = %s""",
                    (pagamento_id,)
                )
                columns = [desc[0] for desc in cur.description]
                row = cur.fetchone()
                return dict(zip(columns, row)) if row else None
        except Exception as e:
            raise Exception(f"Erro ao buscar pagamento: {str(e)}")
        finally:
            conn.close()

    @staticmethod
    def get_consolidated_report(ano, mes):
        """Gera relatório consolidado por dia"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT 
                        EXTRACT(DAY FROM data_registro)::integer as dia,
                        COUNT(*) as quantidade,
                        SUM(valor) as valor
                       FROM Pagamentos
                       WHERE EXTRACT(YEAR FROM data_registro) = %s
                       AND EXTRACT(MONTH FROM data_registro) = %s
                       GROUP BY dia
                       ORDER BY dia""",
                    (ano, mes)
                )
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {str(e)}")
        finally:
            conn.close()

    @staticmethod
    def get_method_report(ano, mes):
        """Gera relatório por método de pagamento"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT 
                        metodo,
                        COUNT(*) as quantidade,
                        SUM(valor) as valor,
                        (SUM(valor) * 100 / (SELECT SUM(valor) FROM Pagamentos 
                            WHERE EXTRACT(YEAR FROM data_registro) = %s
                            AND EXTRACT(MONTH FROM data_registro) = %s) as percentual
                       FROM Pagamentos
                       WHERE EXTRACT(YEAR FROM data_registro) = %s
                       AND EXTRACT(MONTH FROM data_registro) = %s
                       GROUP BY metodo
                       ORDER BY valor DESC""",
                    (ano, mes, ano, mes)
                )
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {str(e)}")
        finally:
            conn.close()

    @staticmethod
    def get_user_report(ano, mes):
        """Gera relatório por apostador"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT 
                        p.apelido,
                        a.Nome as nome,
                        COUNT(*) as quantidade,
                        SUM(p.valor) as valor,
                        (SUM(p.valor) * 100 / (SELECT SUM(valor) FROM Pagamentos 
                            WHERE EXTRACT(YEAR FROM data_registro) = %s
                            AND EXTRACT(MONTH FROM data_registro) = %s) as percentual
                       FROM Pagamentos p
                       JOIN Apostadores a ON p.apelido = a.Apelido
                       WHERE EXTRACT(YEAR FROM p.data_registro) = %s
                       AND EXTRACT(MONTH FROM p.data_registro) = %s
                       GROUP BY p.apelido, a.Nome
                       ORDER BY valor DESC""",
                    (ano, mes, ano, mes)
                )
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {str(e)}")
        finally:
            conn.close()