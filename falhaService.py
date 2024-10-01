
from datetime import datetime

class FalhaService:

    def __init__(self) -> None:
        self.arquivo_cliente = "data/falha_cliente.txt"
        self.arquivo_empresa = "data/falha_empresa.txt"
        pass
    
    def addCliente(self, cod, ini_d, fin_d, motivo):
        linha = f"cod_cliente: {cod} | periodo: {datetime.strftime(ini_d,"%Y-%m-%d %H:%M:%S")};{datetime.strftime(fin_d,"%Y-%m-%d %H:%M:%S")} | motivo: {motivo}\n"
        with open(self.arquivo_cliente, mode='a') as file:
            file.write(linha)
    
    def addEmpresa(self, cnpj, ini_d, fin_d):
        linha = f"cnpj: {cnpj} | periodo: {datetime.strftime(ini_d,"%Y-%m-%d %H:%M:%S")};{datetime.strftime(fin_d,"%Y-%m-%d %H:%M:%S")}\n"
        with open(self.arquivo_empresa, mode='a') as file:
            file.write(linha)