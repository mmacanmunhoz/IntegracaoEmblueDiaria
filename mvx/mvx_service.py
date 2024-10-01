
from mvx.mvx_api import *
from classes import *
from mvx.mvx_util import mvx_sanitize_json
from datetime import datetime, timedelta
import json


class MvxService:

    def __init__(self):
        self.contagem_req_clientes = 0
        self.contagem_req_produtos = 0


    def empresas(self):
        try:
            response = buscar_empresas()
            print(response.status_code)
            if response.status_code != 200:
                return 'ERR: '+ response.text
            
            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content)
            jsonBytes = jsonStr.encode()
            
            return list(json.loads(jsonBytes)['ResponseData'])
        except Exception as e:
            return 'EX: ' + str(e)
        
    def lojas(self, cnpj):
        try:
            response = buscar_lojas(cnpj)
            print(response.status_code)
            if response.status_code != 200:
                return 'ERR: '+ response.text
            
            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content)
            jsonBytes = jsonStr.encode()
            
            return list(json.loads(jsonBytes)['ResponseData'])
        except Exception as e:
            return 'EX: ' + str(e)
        
    def movimentos(self, cnpj,data_ini, data_fin):
        try:
            response = buscar_movimentos(cnpj,data_ini,data_fin)
            if response.status_code != 200:
                return 'ERR: '+ response.text
            
            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content)
            jsonBytes = jsonStr.encode()
            movs = list(json.loads(jsonBytes)['ResponseData'])
            return movs
        except Exception as e:
            return 'EX: ' + str(e)
        
    def movimentosDeOntem(self, cnpj):
        data_ini = datetime.today().date() - timedelta(days=1)
        data_fin = datetime.today().date() - timedelta(seconds=-1)
        return self.movimentos(cnpj,data_ini,data_fin)


    def encontrar_cliente(self,cnpj, codCliente):
        try:
            self.contagem_req_clientes += 1
            response = buscar_cliente(cnpj,codCliente)
            if response.status_code != 200:
                return 'ERR: '+ response.text
            
            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content)
            jsonBytes = jsonStr.encode()
            
            reqs = list(json.loads(jsonBytes)['ResponseData'])
            if len(reqs) > 0:
                mvx_cliente = Cliente(reqs[0])
                return mvx_cliente
        
            return 'Not found'
        except Exception as e:
            return 'EX: ' + str(e)

    def encontrar_produto(self, cnpj, cod):
       
        try:
            self.contagem_req_produtos += 1
            response = buscar_produto(cnpj,cod)
            if response.status_code != 200:
                return 'ERR: '+ response.text
            
            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content)
            jsonBytes = jsonStr.encode()
            
            reqs = list(json.loads(jsonBytes)['ResponseData'])
            if len(reqs) > 0:
                prod = reqs[0]
                return prod
        
            return 'Not found'
        except Exception as e:
            return 'EX: ' + str(e)

    def buscar_todos_os_clientes(self,cnpj, data_i, data_f):
        
        try:
            response = buscar_todos_os_cliente(cnpj,data_i, data_f)
            if response.status_code != 200:
                return 'ERR: '+ response.text

            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content).replace("\\\",","\",").replace("\\","\\\\").replace("\\\\\"","\\\"")
            jsonBytes = jsonStr.encode()
            
            clienteLst = list(json.loads(jsonBytes)['ResponseData'])
            
            clientes = list(filter(lambda x: x['tipo_cadastro'].lower() == 'c',clienteLst))
            creal = 0
            for c in clientes:
                encontrado = next(filter(lambda x: x.cod_cliente == c['cod_cliente'] ,self.LISTA_MVXCLIENTES), None)
                if encontrado == None:
                    mvx_cliente = Cliente(c)
                    self.LISTA_MVXCLIENTES.append(mvx_cliente)
                    creal += 1
        
            return (creal,len(clientes))
        except Exception as e:
            return (0,'EX: ' + str(e))
    


def parse_date(item):
    return datetime.strptime(item.data, "%d/%m/%Y %H:%M:%S")