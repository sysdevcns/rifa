from controllers.apostador_controller import ApostadorController

class WhatsAppService:
    @staticmethod
    def get_whatsapp_link(apelido, numero_jogo, evento_nome, status_jogo):
        apostador = ApostadorController.get_by_apelido(apelido)
        if not apostador or not apostador['DDD'] or not apostador['Telefone']:
            return None
        
        # Remover caracteres não numéricos do telefone
        telefone = ''.join(filter(str.isdigit, apostador['Telefone']))
        
        whatsapp_url = f"https://wa.me/55{apostador['DDD']}{telefone}"
        mensagem = (
            f"Olá {apostador['Nome'].split()[0]}! "
            f"Informações sobre seu jogo:\n\n"
            f"• Número: {numero_jogo}\n"
            f"• Evento: {evento_nome}\n"
            f"• Status: {status_jogo}\n\n"
            f"Obrigado por participar!"
        )
        
        return f"{whatsapp_url}?text={mensagem.replace(' ', '%20').replace('\n', '%0A')}"