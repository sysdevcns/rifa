from services.db_service import DatabaseService

class JogoModel:
    @staticmethod
    def count():
        """Conta total de jogos cadastrados"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM Jogos")
                return cur.fetchone()[0]
        finally:
            conn.close()

    @staticmethod
    def count_by_event(evento_id):
        """Conta jogos de um evento específico"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM Jogos 
                    WHERE evento_id = %s
                """, (evento_id,))
                return cur.fetchone()[0]
        finally:
            conn.close()

    @staticmethod
    def count_by_event_and_status(evento_id, status):
        """Conta jogos por evento e status"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM Jogos 
                    WHERE evento_id = %s AND status = %s
                """, (evento_id, status))
                return cur.fetchone()[0]
        finally:
            conn.close()

    @staticmethod
    def total_amount_by_event(evento_id):
        """Calcula valor total arrecadado por evento"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT SUM(e.Ticket)
                    FROM Jogos j
                    JOIN Eventos e ON j.evento_id = e.id
                    WHERE j.evento_id = %s AND j.status = 'VENDIDO'
                """, (evento_id,))
                return float(cur.fetchone()[0] or 0)
        finally:
            conn.close()

    @staticmethod
    def status_distribution(evento_id):
        """Distribuição de status dos jogos por evento"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT status, COUNT(*) 
                    FROM Jogos 
                    WHERE evento_id = %s
                    GROUP BY status
                """, (evento_id,))
                return {row[0]: row[1] for row in cur.fetchall()}
        finally:
            conn.close()

    @staticmethod
    def top_users_by_event(evento_id, limit=5):
        """Top apostadores por evento"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT j.apelido, a.Nome as nome, COUNT(*) as total_jogos
                    FROM Jogos j
                    JOIN Apostadores a ON j.apelido = a.Apelido
                    WHERE j.evento_id = %s
                    GROUP BY j.apelido, a.Nome
                    ORDER BY total_jogos DESC
                    LIMIT %s
                """, (evento_id, limit))
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def count_by_user(apelido):
        """Conta jogos de um apostador"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM Jogos 
                    WHERE apelido = %s
                """, (apelido,))
                return cur.fetchone()[0]
        finally:
            conn.close()

    @staticmethod
    def get_last_by_user(apelido, limit=10):
        """Obtém últimos jogos de um apostador"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT j.numero, e.Nome as evento, j.status, j.data_venda
                    FROM Jogos j
                    JOIN Eventos e ON j.evento_id = e.id
                    WHERE j.apelido = %s
                    ORDER BY j.data_venda DESC
                    LIMIT %s
                """, (apelido, limit))
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()


    @staticmethod
    def get_by_number(evento_id, numero):
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, evento_id, numero, status, apelido, 
                       data_reserva, data_venda 
                       FROM Jogos 
                       WHERE evento_id = %s AND numero = %s""",
                    (evento_id, numero)
                )
                columns = [desc[0] for desc in cur.description]
                row = cur.fetchone()
                return dict(zip(columns, row)) if row else {'status': 'DISPONIVEL'}
        finally:
            conn.close()
            
    @staticmethod
    def get_by_user(evento_id, apelido):
        """Obtém todos os jogos de um usuário em um evento"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, numero, status, data_reserva, data_venda
                    FROM Jogos
                    WHERE evento_id = %s AND apelido = %s
                    ORDER BY numero""",
                    (evento_id, apelido)
                )
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_reserved_by_user(apelido):
        """Obtém todos os jogos reservados por um apostador"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        j.id,
                        j.numero,
                        e.Nome as evento_nome,
                        e.Ticket as valor,
                        j.data_reserva
                    FROM Jogos j
                    JOIN Eventos e ON j.evento_id = e.id
                    WHERE j.apelido = %s AND j.status = 'RESERVADO'
                    ORDER BY e.Nome, j.numero
                """, (apelido,))
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()
            
    
    @staticmethod
    def reserve_number(evento_id, numero, apelido):
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO Jogos 
                    (evento_id, numero, status, apelido, data_reserva)
                    VALUES (%s, %s, 'RESERVADO', %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (evento_id, numero) 
                    DO UPDATE SET status = 'RESERVADO', 
                                apelido = EXCLUDED.apelido,
                                data_reserva = CURRENT_TIMESTAMP
                    RETURNING id""",
                    (evento_id, numero, apelido)
                )
                conn.commit()
                return cur.fetchone()[0]
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao reservar número: {str(e)}")
        finally:
            conn.close()
    
    @staticmethod
    def cancel_reservation(evento_id, numero):
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE Jogos 
                    SET status = 'DISPONIVEL', 
                        apelido = NULL,
                        data_reserva = NULL
                    WHERE evento_id = %s AND numero = %s
                    RETURNING id""",
                    (evento_id, numero)
                )
                conn.commit()
                return cur.fetchone()[0] if cur.rowcount > 0 else None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao cancelar reserva: {str(e)}")
        finally:
            conn.close()
