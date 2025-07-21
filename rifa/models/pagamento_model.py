from services.db_service import DatabaseService

class PagamentoModel:
    @staticmethod
    def create(numero, apelido, valor, metodo, observacoes, jogos):
        """Registra um novo pagamento no banco de dados"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                # Insere o pagamento
                cur.execute(
                    """INSERT INTO Pagamentos 
                    (numero, apelido, valor, metodo, observacoes) 
                    VALUES (%s, %s, %s, %s, %s) 
                    RETURNING id""",
                    (numero, apelido, valor, metodo, observacoes)
                )
                payment_id = cur.fetchone()[0]
                
                # Atualiza o status dos jogos
                for numero_jogo in jogos:
                    cur.execute(
                        """UPDATE Jogos 
                        SET status = 'VENDIDO', 
                            data_venda = CURRENT_TIMESTAMP 
                        WHERE numero = %s""",
                        (numero_jogo,)
                    )
                
                conn.commit()
                return payment_id
        finally:
            conn.close()


    @staticmethod
    def total_amount(start_date=None, end_date=None):
        """Soma total de pagamentos no período"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = "SELECT SUM(valor) FROM Pagamentos WHERE 1=1"
                params = []
                
                if start_date:
                    query += " AND data_registro >= %s"
                    params.append(start_date)
                if end_date:
                    query += " AND data_registro <= %s"
                    params.append(end_date)
                
                cur.execute(query, params)
                return float(cur.fetchone()[0] or 0)
        finally:
            conn.close()

    @staticmethod
    def sum_by_method(start_date=None, end_date=None):
        """Soma pagamentos por método no período"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT metodo, SUM(valor) 
                    FROM Pagamentos 
                    WHERE 1=1
                """
                params = []
                
                if start_date:
                    query += " AND data_registro >= %s"
                    params.append(start_date)
                if end_date:
                    query += " AND data_registro <= %s"
                    params.append(end_date)
                
                query += " GROUP BY metodo"
                cur.execute(query, params)
                return {row[0]: float(row[1] or 0) for row in cur.fetchall()}
        finally:
            conn.close()

    @staticmethod
    def total_amount_by_user(apelido):
        """Soma total gasto por um apostador"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT SUM(valor)
                    FROM Pagamentos
                    WHERE Apelido = %s
                """, (apelido,))
                return float(cur.fetchone()[0] or 0)
        finally:
            conn.close()


    @staticmethod    
    def get_reserved_by_user(apelido):
        """Obtém todos os jogos reservados por um usuário, com informações do evento"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT j.id, j.numero, j.evento_id, e.nome as evento_nome, 
                    j.data_reserva, e.ticket as valor
                    FROM Jogos j
                    JOIN Eventos e ON j.evento_id = e.id
                    WHERE j.apelido = %s AND j.status = 'RESERVADO'
                    ORDER BY e.nome, j.numero""",
                    (apelido,)
                )
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao buscar jogos reservados: {str(e)}")
        finally:
            conn.close()