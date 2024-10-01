
from emblue.emblue_api import *
from shared.log import log

class EmblueService:

    def __init__(self, token_auth, login_user, login_psw):
        self.api = EmblueApi(token_auth,login_user,login_psw)
        self.token_res = self.api.set_token()
        
    
    def atualizar_contato(self, mvx_cliente):
        existe = mvx_cliente.emblue_email_id if mvx_cliente.emblue_email_id > 0 else self.api.existe_contato(mvx_cliente.email_cliente)
        if(isinstance(existe,str)):
            erro = existe
            return erro
        elif existe == -1:
            resp = self.api.criar_contato(mvx_cliente)
            if(isinstance(resp,str)):
                erro = resp
                return erro
            else:
                mvx_cliente.emblue_email_id = int(resp)
        else:
            if mvx_cliente.emblue_email_id <= 0:
                mvx_cliente.emblue_email_id = existe

            resp = self.api.editar_contato(mvx_cliente)
            if(isinstance(resp,str)):
                erro = resp
                return erro
        return True

