from services.db_service import DatabaseService

class FixoModel:
    @staticmethod
    def create(apelido, numero, grupo=None, status="Ativo"):
        """Cria um novo jogo fixo no banco de dados"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO Fixos 
                    (apelido, numero, grupo, status) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING id""",
                    (apelido, numero, grupo, status)
                )
                conn.commit()
                return cur.fetchone()[0]
        finally:
            conn.close()


    @staticmethod
    def update(fixo_id, **kwargs):
        """Atualiza um jogo fixo"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = "UPDATE Fixos SET "
                params = []
                updates = []
                
                for key, value in kwargs.items():
                    if value is not None:
                        updates.append(f"{key} = %s")
                        params.append(value)
                
                if not updates:
                    raise ValueError("Nenhum campo para atualizar")
                
                query += ", ".join(updates) + " WHERE id = %s"
                params.append(fixo_id)
                
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao atualizar jogo fixo: {str(e)}")
        finally:
            conn.close()


    @staticmethod
    def search(**filters):
        """Busca jogos fixos com filtros"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = """SELECT id, apelido, numero, grupo, status, data_registro 
                        FROM Fixos WHERE 1=1"""
                params = []
                
                # Filtros opcionais
                if filters.get('apelido'):
                    query += " AND apelido = %s"
                    params.append(filters['apelido'])
                if filters.get('status'):
                    query += " AND status = %s"
                    params.append(filters['status'])
                if filters.get('grupo'):
                    query += " AND grupo ILIKE %s"
                    params.append(f"%{filters['grupo']}%")
                if filters.get('numero'):
                    query += " AND numero = %s"
                    params.append(filters['numero'])
                
                query += " ORDER BY apelido, numero"
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()
    
    @staticmethod
    def apply_to_event(evento_id, apelido=None, grupo=None):
        """Aplica jogos fixos a um evento específico"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                # 1. Obter jogos fixos que correspondem aos filtros
                query = """SELECT id, apelido, numero FROM Fixos 
                        WHERE status = 'Ativo'"""
                params = []
                
                if apelido:
                    query += " AND apelido = %s"
                    params.append(apelido)
                if grupo:
                    query += " AND grupo ILIKE %s"
                    params.append(f"%{grupo}%")
                    
                query += " ORDER BY apelido, numero"
                cur.execute(query, params)
                fixos = cur.fetchall()
                
                applied = 0
                skipped = 0
                failed = 0
                
                # 2. Aplicar cada jogo ao evento
                for fixo in fixos:
                    try:
                        # Verificar se já existe no evento
                        cur.execute(
                            """SELECT 1 FROM Jogos 
                            WHERE evento_id = %s AND numero = %s""",
                            (evento_id, fixo[2])
                        )
                        if cur.fetchone():
                            skipped += 1
                            continue
                            
                        # Criar registro na tabela Jogos
                        cur.execute(
                            """INSERT INTO Jogos 
                            (evento_id, numero, status, apelido, data_reserva)
                            VALUES (%s, %s, 'RESERVADO', %s, CURRENT_TIMESTAMP)""",
                            (evento_id, fixo[2], fixo[1])
                        )
                        applied += 1
                    except Exception:
                        failed += 1
                        
                conn.commit()
                return {
                    'applied': applied,
                    'skipped': skipped,
                    'failed': failed
                }
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao aplicar jogos ao evento: {str(e)}")
        finally:
            conn.close()

    
    @staticmethod
    def get_all_active():
        """Obtém todos os jogos fixos ativos"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, apelido, numero, grupo, status 
                    FROM Fixos WHERE status = 'Ativo' 
                    ORDER BY apelido, numero"""
                )
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(fixo_id):
        """Obtém um jogo fixo pelo ID"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, apelido, numero, grupo, status, data_registro 
                    FROM Fixos WHERE id = %s""",
                    (fixo_id,)
                )
                columns = [desc[0] for desc in cur.description]
                row = cur.fetchone()
                return dict(zip(columns, row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_fixos_to_apply(apelido=None, grupo=None):
        """Obtém jogos fixos para aplicar a eventos com filtros opcionais"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = """SELECT id, apelido, numero FROM Fixos 
                        WHERE status = 'Ativo'"""
                params = []
                
                if apelido:
                    query += " AND apelido = %s"
                    params.append(apelido)
                if grupo:
                    query += " AND grupo ILIKE %s"
                    params.append(f"%{grupo}%")
                    
                query += " ORDER BY apelido, numero"
                cur.execute(query, params)
                return cur.fetchall()
        finally:
            conn.close()

    
    @staticmethod
    def batch_update_status(apelido=None, grupo=None, status='Ativo'):
        """Atualiza status em lote com filtros"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = "UPDATE Fixos SET status = %s"
                params = [status]
                
                conditions = []
                if apelido:
                    conditions.append("apelido = %s")
                    params.append(apelido)
                if grupo:
                    conditions.append("grupo ILIKE %s")
                    params.append(f"%{grupo}%")
                    
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                    
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao atualizar status em lote: {str(e)}")
        finally:
            conn.close()