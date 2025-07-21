from models.evento_model import EventoModel
from models.apostador_model import ApostadorModel
from models.jogo_model import JogoModel
from models.pagamento_model import PagamentoModel

class RelatorioController:
    @staticmethod
    def get_general_summary(start_date, end_date):
        """Gera um resumo geral do sistema"""
        return {
            "total_eventos": EventoModel.count(),
            "apostadores_ativos": ApostadorModel.count_active(),
            "total_jogos": JogoModel.count(),
            "total_pagamentos": PagamentoModel.total_amount(start_date, end_date),
            "eventos_por_status": EventoModel.count_by_status(),
            "pagamentos_por_metodo": PagamentoModel.sum_by_method(start_date, end_date)
        }
    

    @staticmethod
    def get_events_list():
        """Obtém lista de eventos para seleção"""
        return EventoModel.get_all()
    

    @staticmethod
    def get_event_report(evento_id):
        """Gera relatório detalhado de um evento"""
        return {
            "evento": EventoModel.get_by_id(evento_id),
            "total_jogos": JogoModel.count_by_event(evento_id),
            "jogos_disponiveis": JogoModel.count_by_event_and_status(evento_id, "DISPONIVEL"),
            "jogos_reservados": JogoModel.count_by_event_and_status(evento_id, "RESERVADO"),
            "jogos_vendidos": JogoModel.count_by_event_and_status(evento_id, "VENDIDO"),
            "arrecadacao_total": JogoModel.total_amount_by_event(evento_id),
            "distribuicao_jogos": JogoModel.status_distribution(evento_id),
            "top_apostadores": JogoModel.top_users_by_event(evento_id)
        }
    

    @staticmethod
    def get_users_list():
        """Obtém lista de apostadores para seleção"""
        return ApostadorModel.get_all_active()
    

    @staticmethod
    def get_user_report(apelido):
        """Gera relatório detalhado de um apostador"""
        return {
            "apostador": ApostadorModel.get_by_apelido(apelido),
            "total_jogos": JogoModel.count_by_user(apelido),
            "total_gasto": PagamentoModel.total_amount_by_user(apelido),
            "ultimos_jogos": JogoModel.get_last_by_user(apelido, limit=10)
        }