

from classes import Cliente
from shared.log import log


class TempClienteMovimentoService:

    def __init__(self) -> None:
        self.cliente_mov_dic = dict()
        pass

    def add(self, clienteCod, mvxMov):
        existente = self.cliente_mov_dic[clienteCod] if clienteCod in self.cliente_mov_dic else None
        if(existente is None):
            existente = []
        existente.append(mvxMov)
        self.cliente_mov_dic[clienteCod] = existente

class TempClientesService:

    def __init__(self) -> None:
        self.clientes = list()
        pass

    def add(self, cliente):
        self.clientes.append(cliente)

    
    def encontrar(self, cod_cliente):
        return next(filter(lambda x: x.cod_cliente == cod_cliente, self.clientes ), None)

class BlacklistClienteService:

    def __init__(self, filePath) -> None:
        self.blacklist_clientes_cod = list()
        self.filePath = filePath

        log("Carregando Clientes Blacklist")
        with open(filePath, 'r') as file:
            self.blacklist_clientes_cod = list(map(lambda x : x.replace('\n',''), file.readlines()))

        pass
     
    def add(self, cod_cliente):
        self.blacklist_clientes_cod.append(cod_cliente)
        log(f"Cliente adicionado a Blacklist {cod_cliente}")

    def encontrar(self, cod_cliente):
        return next(filter(lambda x: x == cod_cliente, self.blacklist_clientes_cod), None)
    
    def salvar(self):
        with open(self.filePath, 'w') as file:
            file.writelines(map(lambda x : f"{x}\n",self.blacklist_clientes_cod))

class ClienteIdService:

    def __init__(self, filePath) -> None:
        self.mvxCod_emblueId_dict = dict()
        self.mvxCod_email_dict = dict()
        self.filePath = filePath

        log("Carregando Clientes ID MVX vs Emblue")
        with open(filePath, 'r') as file:
            lines = list(map(lambda x : x.replace('\n',''), file.readlines()))
            for l in lines:
                lsplit = l.split(";")
                self.mvxCod_emblueId_dict[lsplit[0]] = lsplit[1]
                self.mvxCod_email_dict[lsplit[0]] = lsplit[2]

        pass
     
    def add(self, cod_cliente, emblueId, email):
        self.mvxCod_emblueId_dict[cod_cliente] = emblueId
        self.mvxCod_email_dict[cod_cliente] = email

    def encontrar(self, cod_cliente):
        if cod_cliente in self.mvxCod_emblueId_dict:
            emblueId = int(self.mvxCod_emblueId_dict[cod_cliente])
            return (emblueId, self.mvxCod_email_dict[cod_cliente])
        return (None, None)
    
    def salvar(self):
        with open(self.filePath, 'w') as file:
            file.writelines(map(lambda k: f"{k};{self.mvxCod_emblueId_dict[k]};{self.mvxCod_email_dict[k]}\n", self.mvxCod_emblueId_dict.keys()))