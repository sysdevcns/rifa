from services.db_service import DatabaseService

class EventoModel:
    @staticmethod
    def create(**kwargs):
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO Eventos 
                    (Nome, Tipo, Divulgacao, Ticket, Premio, Trave, Resultado, Descricao, Concurso, Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id""",
                    (kwargs['nome'], kwargs['tipo'], kwargs['divulgacao'], kwargs['ticket'],
                     kwargs['premio'], kwargs['trave'], kwargs.get('resultado'), 
                     kwargs.get('descricao'), kwargs.get('concurso'), kwargs.get('status', 'Ativo'))
                )
                
                evento_id = cur.fetchone()[0]
                conn.commit()
                return evento_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def update(evento_id, **kwargs):
        """Atualiza um evento existente"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    UPDATE Eventos SET
                        Nome = %s,
                        Tipo = %s,
                        Divulgacao = %s,
                        Ticket = %s,
                        Premio = %s,
                        Trave = %s,
                        Descricao = %s,
                        Concurso = %s
                    WHERE id = %s
                """
                params = (
                    kwargs['nome'],
                    kwargs['tipo'],
                    kwargs['divulgacao'],
                    kwargs['ticket'],
                    kwargs['premio'],
                    kwargs.get('trave'),
                    kwargs.get('descricao'),
                    kwargs.get('concurso'),
                    evento_id
                )
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise e  # Apenas levanta a exceção para ser tratada no controller
        finally:
            conn.close()

    @staticmethod
    def count():
        """Conta o total de eventos cadastrados"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM Eventos")
                return cur.fetchone()[0]
        finally:
            conn.close()

    @staticmethod
    def count_by_status():
        """Conta eventos agrupados por status"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT Status, COUNT(*) 
                    FROM Eventos 
                    GROUP BY Status
                """)
                return {row[0]: row[1] for row in cur.fetchall()}
        finally:
            conn.close()


    @staticmethod
    def get_all():
        """Obtém todos os eventos com nomes de campos padronizados"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id,
                        Nome as nome,
                        Tipo as tipo,
                        Divulgacao as data_divulgacao,
                        Ticket as valor_ticket,
                        Premio as valor_premio,
                        Trave as valor_trave,
                        Status as status
                    FROM Eventos
                    ORDER BY Nome
                """)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao buscar eventos: {str(e)}")
        finally:
            conn.close()


    @staticmethod
    def get_by_id(evento_id):
        """Obtém um evento específico pelo ID"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, Nome as nome, Tipo, Divulgacao as data_divulgacao,
                    Ticket as valor_ticket, Premio as valor_premio, Trave AS valor_trave, Status
                    FROM Eventos
                    WHERE id = %s
                """, (evento_id,))
                columns = [desc[0] for desc in cur.description]
                row = cur.fetchone()
                return dict(zip(columns, row)) if row else None
        finally:
            conn.close()


    @staticmethod
    def get_active_events():
        """Obtém eventos ativos com nomes de campos padronizados"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id, 
                        Nome AS nome,
                        Tipo, 
                        Divulgacao as data_divulgacao,
                        Ticket AS valor_ticket,
                        Premio AS valor_premio,
                        Trave AS valor_trave,
                        Status
                    FROM Eventos 
                    WHERE Status = 'Ativo'
                    ORDER BY Nome
                """)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao buscar eventos ativos: {str(e)}")
        finally:
            conn.close()    


    @staticmethod
    def update_status(evento_id, novo_status):
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE Eventos SET Status = %s WHERE id = %s",
                    (novo_status, evento_id)
                )
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
            
