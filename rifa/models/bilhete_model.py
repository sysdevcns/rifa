from services.db_service import DatabaseService

class BilheteModel:
    @staticmethod
    def create(numero, tipo, lote=None, status="Disponível", observacoes=None):
        """Cria um novo bilhete no banco de dados"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO Bilhetes 
                    (numero, tipo, lote, status, observacoes) 
                    VALUES (%s, %s, %s, %s, %s) 
                    RETURNING id""",
                    (numero, tipo, lote, status, observacoes)
                )
                conn.commit()
                return cur.fetchone()[0]
        finally:
            conn.close()

    
    @staticmethod
    def search(**filters):
        """Busca bilhetes com filtros"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = """SELECT id, numero, tipo, lote, status, observacoes, 
                        data_cadastro FROM Bilhetes WHERE 1=1"""
                params = []
                
                if filters.get('numero'):
                    query += " AND numero ILIKE %s"
                    params.append(f"%{filters['numero']}%")
                    
                if filters.get('tipo') and filters['tipo'] != 'Todos':
                    query += " AND tipo = %s"
                    params.append(filters['tipo'])
                    
                if filters.get('status') and filters['status'] != 'Todos':
                    query += " AND status = %s"
                    params.append(filters['status'])
                    
                if filters.get('lote'):
                    query += " AND lote ILIKE %s"
                    params.append(f"%{filters['lote']}%")
                    
                if filters.get('data_inicio'):
                    query += " AND data_cadastro >= %s"
                    params.append(filters['data_inicio'])
                    
                if filters.get('data_fim'):
                    query += " AND data_cadastro <= %s"
                    params.append(filters['data_fim'])
                
                query += " ORDER BY data_cadastro DESC"
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao buscar bilhetes: {str(e)}")
        finally:
            conn.close()

    
    @staticmethod
    def get_available(filters=None):
        """Obtém bilhetes disponíveis com filtros opcionais"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                query = """SELECT id, numero, tipo, lote, status, observacoes 
                          FROM Bilhetes WHERE status = 'Disponível'"""
                params = []
                
                if filters:
                    if filters.get('tipo'):
                        query += " AND tipo = %s"
                        params.append(filters['tipo'])
                    if filters.get('lote'):
                        query += " AND lote = %s"
                        params.append(filters['lote'])
                
                query += " ORDER BY numero"
                cur.execute(query, params)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()


    @staticmethod
    def get_stats():
        """Retorna estatísticas gerais sobre bilhetes"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'Disponível' THEN 1 ELSE 0 END) as disponiveis,
                        SUM(CASE WHEN status = 'Reservado' THEN 1 ELSE 0 END) as reservados,
                        SUM(CASE WHEN status = 'Vendido' THEN 1 ELSE 0 END) as vendidos
                    FROM Bilhetes
                """)
                result = cur.fetchone()
                return {
                    'total': result[0],
                    'disponiveis': result[1],
                    'disponiveis_pct': (result[1]/result[0])*100 if result[0] > 0 else 0,
                    'reservados': result[2],
                    'reservados_pct': (result[2]/result[0])*100 if result[0] > 0 else 0,
                    'vendidos': result[3],
                    'vendidos_pct': (result[3]/result[0])*100 if result[0] > 0 else 0
                }
        finally:
            conn.close()


    @staticmethod
    def get_stats_by_type():
        """Obtém estatísticas de bilhetes por tipo"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        tipo,
                        COUNT(*) as quantidade,
                        ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM bilhetes)), 2) as percentual
                    FROM bilhetes
                    GROUP BY tipo
                    ORDER BY quantidade DESC
                """)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao buscar estatísticas por tipo: {str(e)}")
        finally:
            conn.close()