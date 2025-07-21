from models.apostador_model import ApostadorModel

class ApostadorController:
    @staticmethod
    def create(nome, apelido, ddd=None, telefone=None, email=None, endereco=None):
        try:
            # Verifica se o apelido já existe
            if ApostadorController.apelido_exists(apelido):
                raise ValueError(f"O apelido '{apelido}' já está em uso")
                
            # Validação adicional
            if len(apelido) < 3:
                raise ValueError("O apelido deve ter pelo menos 3 caracteres")
                
            return ApostadorModel.create(
                nome=nome,
                apelido=apelido,
                ddd=ddd,
                telefone=telefone,
                email=email,
                endereco=endereco
            )
        except Exception as e:
            raise Exception(f"Erro ao criar apostador: {str(e)}")
        
    @staticmethod
    def search(nome=None, apelido=None, status=None, only_active=False):
        try:
            return ApostadorModel.search(
                nome=nome,
                apelido=apelido,
                status=status,
                only_active=only_active
            )
        except Exception as e:
            raise Exception(f"Erro ao buscar apostadores: {str(e)}")
        
    @staticmethod
    def update(apelido, **kwargs):
        try:
            return ApostadorModel.update(apelido, **kwargs)
        except Exception as e:
            raise Exception(f"Erro ao atualizar apostador: {str(e)}")
        
    @staticmethod
    def deactivate(apelido):
        try:
            # Verificar se o apostador existe antes de desativar
            if not ApostadorModel.get_by_apelido(apelido):
                raise ValueError(f"Apostador com apelido '{apelido}' não encontrado")
                
            return ApostadorModel.deactivate(apelido)
        except Exception as e:
            raise Exception(f"Erro ao desativar apostador: {str(e)}")

    @staticmethod
    def count_active():
        """Conta o número de apostadores ativos"""
        try:
            return ApostadorModel.count_active()
        except Exception as e:
            raise Exception(f"Erro ao contar apostadores ativos: {str(e)}")        

    @staticmethod
    def apelido_exists(apelido):
        return ApostadorModel.get_by_apelido(apelido) is not None

    @staticmethod
    def get_by_apelido(apelido):
        try:
            return ApostadorModel.get_by_apelido(apelido)
        except Exception as e:
            raise Exception(f"Erro ao buscar apostador: {str(e)}")

    @staticmethod
    def get_all_active():
        """Obtém todos os apostadores ativos"""
        try:
            return ApostadorModel.search(status='Ativo')
        except Exception as e:
            raise Exception(f"Erro ao buscar apostadores ativos: {str(e)}")