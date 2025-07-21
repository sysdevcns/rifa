from services.db_service import DatabaseService
from models.evento_model import EventoModel
from .jogo_controller import JogoController

class EventoController:
    @staticmethod
    def create(**kwargs):
            try:
                return EventoModel.create(**kwargs)
            except Exception as e:
                raise Exception(f"Erro ao criar evento: {str(e)}")

    @staticmethod
    def update(evento_id, **kwargs):
        try:
            return EventoModel.update(evento_id, **kwargs)
        except Exception as e:
            raise Exception(f"Erro ao atualizar evento: {str(e)}")
        
    @staticmethod
    def count():
        """Conta o total de eventos"""
        try:
            return EventoModel.count()
        except Exception as e:
            raise Exception(f"Erro ao contar eventos: {str(e)}")

    @staticmethod
    def count_by_status():
        """Conta eventos por status"""
        try:
            return EventoModel.count_by_status()
        except Exception as e:
            raise Exception(f"Erro ao contar eventos por status: {str(e)}")
        
    @staticmethod
    def update_status(evento_id, novo_status):
        try:
            return EventoModel.update_status(evento_id, novo_status)
        except Exception as e:
            raise Exception(f"Erro ao atualizar status: {str(e)}")        
            
    @staticmethod
    def get_all(filtro=None):
        try:
            eventos = EventoModel.get_all()
            if filtro:
                filtro = filtro.lower()
                return [e for e in eventos 
                       if filtro in e['nome'].lower() or 
                       filtro in e['tipo'].lower()]
            return eventos
        except Exception as e:
            raise Exception(f"Erro ao buscar eventos: {str(e)}")
    
    @staticmethod
    def get_by_id(evento_id):
        try:
            return EventoModel.get_by_id(evento_id)
        except Exception as e:
            raise Exception(f"Erro ao buscar evento: {str(e)}")

    @staticmethod
    def get_active_events():
        """Obtém todos os eventos ativos"""
        try:
            return EventoModel.get_active_events()
        except Exception as e:
            raise Exception(f"Erro ao buscar eventos ativos: {str(e)}")

    @staticmethod
    def get_active_event_id():
        """Obtém o ID do primeiro evento ativo encontrado"""
        try:
            eventos = EventoModel.get_active_events()
            return eventos[0]['id'] if eventos else None
        except Exception as e:
            raise Exception(f"Erro ao buscar evento ativo: {str(e)}")