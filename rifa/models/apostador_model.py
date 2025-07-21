from services.db_service import DatabaseService

class ApostadorModel:
    @staticmethod
    def create(nome, apelido, ddd=None, telefone=None, email=None, endereco=None):
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO Apostadores 
                    (Nome, Apelido, DDD, Telefone, Email, Endereco) 
                    VALUES (%s, %s, %s, %s, %s, %s) 
                    RETURNING id""",
                    (nome, apelido, ddd, telefone, email, endereco)
                )
                apostador_id = cur.fetchone()[0]
                conn.commit()
                return apostador_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


    @staticmethod
    def update(apelido, **kwargs):
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = "UPDATE Apostadores SET "
                params = []
                updates = []
                
                for key, value in kwargs.items():
                    if value is not None:
                        updates.append(f"{key} = %s")
                        params.append(value)
                
                if not updates:
                    raise ValueError("Nenhum campo para atualizar")
                
                query += ", ".join(updates) + " WHERE Apelido = %s"
                params.append(apelido)
                
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


    @staticmethod
    def deactivate(apelido):
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE Apostadores SET Status = 'Inativo' WHERE Apelido = %s",
                    (apelido,)
                )
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


    @staticmethod
    def search(nome=None, apelido=None, status=None, only_active=False):
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = """SELECT id, Nome as nome, Apelido as apelido, DDD as ddd,
                        Telefone as telefone, Email as email, Endereco as endereco,
                        Status as status 
                        FROM Apostadores WHERE 1=1"""
                params = []
                
                if nome:
                    query += " AND Nome ILIKE %s"
                    params.append(f"%{nome}%")
                
                if apelido:
                    query += " AND Apelido ILIKE %s"
                    params.append(f"%{apelido}%")
                
                if status:
                    query += " AND Status = %s"
                    params.append(status)
                elif only_active:
                    query += " AND Status = 'Ativo'"
                
                query += " ORDER BY Nome"
                
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()


    @staticmethod
    def count_active():
        """Conta apostadores ativos"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM Apostadores 
                    WHERE Status = 'Ativo'
                """)
                return cur.fetchone()[0]
        finally:
            conn.close()

    @staticmethod
    def get_all_active():
        """Obtém todos os apostadores ativos"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, Nome as nome, Apelido as apelido, DDD as ddd,
                    Telefone as telefone, Email as email, Status
                    FROM Apostadores
                    WHERE Status = 'Ativo'
                    ORDER BY Nome
                """)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_by_apelido(apelido):
        """Obtém apostador pelo apelido"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, Nome as nome, Apelido as apelido, DDD as ddd,
                    Telefone as telefone, Email as email, Status
                    FROM Apostadores
                    WHERE Apelido = %s
                """, (apelido,))
                columns = [desc[0] for desc in cur.description]
                row = cur.fetchone()
                return dict(zip(columns, row)) if row else None
        finally:
            conn.close()