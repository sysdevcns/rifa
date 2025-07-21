from services.db_service import DatabaseService
from models.jogo_model import JogoModel
from .fixo_controller import FixoController
from .pagamento_controller import PagamentoController

class JogoController:
    @staticmethod
    def create_for_event(evento_id):
        """Cria todos os números (000-999) para um novo evento"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                # Verificar se já existem jogos para este evento
                cur.execute("SELECT COUNT(*) FROM Jogos WHERE evento_id = %s", (evento_id,))
                if cur.fetchone()[0] > 0:
                    raise Exception("Jogos já criados para este evento")
                
                # Inserir todos os números de 000 a 999
                for num in range(1000):
                    num_str = f"{num:03d}"
                    cur.execute(
                        "INSERT INTO Jogos (evento_id, numero) VALUES (%s, %s)",
                        (evento_id, num_str)
                        )
                
                # Reservar números para jogadores fixos
                fixos = FixoController.get_all_active()
                for fixo in fixos:
                    try:
                        cur.execute(
                            """UPDATE Jogos 
                            SET status = 'RESERVADO', 
                                apelido = %s 
                            WHERE evento_id = %s AND numero = %s""",
                            (fixo['apelido'], evento_id, fixo['numero'])
                        )
                        
                        # Criar registro de pagamento pendente
                        PagamentoController.create(
                            numero=f"FIXO-{evento_id}-{fixo['numero']}",
                            apelido=fixo['apelido'],
                            valor=0,  # Será atualizado depois
                            metodo="FIXO",
                            observacoes=f"Jogo fixo {fixo['numero']}",
                            jogos=[fixo['numero']]
                        )
                    except Exception as e:
                        print(f"Erro ao reservar número fixo {fixo['numero']}: {str(e)}")
                
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao criar jogos para o evento: {str(e)}")
        finally:
            conn.close()

    @staticmethod
    def reserve_number(evento_id, numero, apelido):
        """Reserva um número para um apostador"""
        return JogoModel.reserve_number(evento_id, numero, apelido)
    
    @staticmethod
    def cancel_reservation(evento_id, numero):
        """Cancela uma reserva"""
        return JogoModel.cancel_reservation(evento_id, numero)
            
    @staticmethod
    def get_user_games(evento_id, apelido):
        """Obtém todos os jogos de um usuário em um evento"""
        return JogoModel.get_by_user(evento_id, apelido)
            
    @staticmethod
    def get_game_info(evento_id, numero):
        """Obtém informações sobre um jogo específico"""
        return JogoModel.get_by_number(evento_id, numero)
        

    @staticmethod
    def get_reserved_games(apelido):
        """Obtém jogos reservados por um apostador"""
        try:
            return JogoModel.get_reserved_by_user(apelido)
        except Exception as e:
            raise Exception(f"Erro ao buscar jogos reservados: {str(e)}")

        
    @staticmethod
    def get_all_by_event(evento_id):
        """Obtém todos os jogos de um evento específico"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, numero, status, apelido, 
                       data_reserva, data_venda 
                       FROM Jogos 
                       WHERE evento_id = %s
                       ORDER BY numero""",
                    (evento_id,)
                )
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()