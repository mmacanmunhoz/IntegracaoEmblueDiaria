


import requests
import json
from classes import *
from shared.codigo_pais import encontrar_cod, encontrar_pais

class EmblueApi:

    def __init__(self, token_auth, login_user, login_psw):
        self.token_auth = token_auth
        self.token = ''
        self.login_user = login_user
        self.login_psw = login_psw
        pass

    def http_post(self, url, content):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json; charset=utf-8',
        }
        response = requests.post(url, data=content, headers=headers)
        return response

    def set_token(self):
        content = {
            "User": self.login_user,
            "Pass": self.login_psw,
            "Token": self.token_auth
        }

        try:
            response = self.http_post('https://api.embluemail.com/Services/Emblue3Service.svc/json/Authenticate', json.dumps(content))
            if response.status_code != 200:
                return f'set_token err: {response.text}'
            
            authJson = json.loads(response.content)
            self.token = authJson['Token']
            return True
        except Exception as e:
            return "set_token ex: "+ str(e)
        
    def existe_contato(self, email):
        content = {
            "Search": email,
            "Order": "asc",
            "GroupId": "0",
            "Token": self.token
        }

        try:
            response = self.http_post('https://api.embluemail.com/Services/EmBlue3Service.svc/Json/SearchContact?=',json.dumps(content))
            if response.status_code != 200:
                return "Err: "+ response.text
            
            usuarios = list(json.loads(response.content))
            if(len(usuarios)>0):
                return int(usuarios[0]['EmailId'])
            return -1
        except Exception as e:
            return "Ex "+ str(e)

    def criar_contato(self, mvx_cliente):
        content = {
            "Email": mvx_cliente.email_cliente,
            "EditCustomFields": self.montar_campos(mvx_cliente),
            "Token": self.token
        }

        try:
            response = self.http_post('https://api.embluemail.com/Services/EmBlue3Service.svc/Json/NewContact',json.dumps(content))
            if response.status_code != 200:
                return "Err: "+ response.text
            return json.loads(response.content)['EmailId']
        except Exception as e:
            return "Ex "+ str(e)
        
    def editar_contato(self, mvx_cliente):
        content = {
            "EmailId": str(mvx_cliente.emblue_email_id),
            "EditedFields": self.montar_campos(mvx_cliente),
            "Token": self.token
        }


        try:
            response = self.http_post('https://api.embluemail.com/Services/EmBlue3Service.svc/Json/EditCustomFieldsOneContact',json.dumps(content))
            if response.status_code != 200:
                return "Err: "+ response.text
            return True
        except Exception as e:
            return "Ex "+ str(e)

   
    def buscar_cliente(self, email_id):



        content = {
            "EmailId": email_id,
            "Token": self.token
        }

        try:
            response = self.http_post('https://api.embluemail.com/Services/EmBlue3Service.svc/Json/GetCustomFieldsByEmail',json.dumps(content))
            if response.status_code != 200:
                return "Err: "+ response.text
            
            fields = list(json.loads(response.content))
            return self.montar_cliente(fields, email_id)
        except Exception as e:
            return "Ex "+ str(e)
    
        

    def montar_campos(self, mvx_cliente):
        campo_esqueleto = "{0}:|:{1}:|:1"

        campos = {
            'nombre': mvx_cliente.nome_cliente if len(mvx_cliente.nome_cliente) > 0 else mvx_cliente.razao_cliente,
            'CPF': mvx_cliente.doc_cliente,
            'CNPJ': mvx_cliente.cnpj,
            'sexo': mvx_cliente.sexo,
            'telefono_1': mvx_cliente.cel_cliente,
            'cumpleanios': mvx_cliente.data_nascimento,
            'pais': encontrar_pais(mvx_cliente.pais),
            'ciudad': mvx_cliente.cidade_cliente, 
            'Estado': mvx_cliente.uf_cliente,
            'Produto_Um': '',
            'DataProduto_Um': '',
            'Categoria_Um': '',
            'Departamento_Um': '',
            'Loja_Um': '',
            'Canal_Um': '',
            'Produto_Dois': '',
            'DataProduto_Dois': '',
            'Categoria_Dois': '',
            'Departamento_Dois': '',
            'Loja_Dois': '',
            'Canal_Dois': '',
            'Produto_Tres': '',
            'DataProduto_Tres': '',
            'Categoria_Tres': '',
            'Departamento_Tres': '',
            'Loja_Tres': '',
            'Canal_Tres': '',
            'Produto_Quatro': '',
            'DataProduto_Quatro': '',
            'Categoria_Quatro': '',
            'Departamento_Quatro': '',
            'Loja_Quatro': '',
            'Canal_Quatro': '',
            'Produto_Cinco': '',
            'DataProduto_Cinco': '',
            'Categoria_Cinco': '',
            'Departamento_Cinco': '',
            'Loja_Cinco': '',
            'Canal_Cinco': ''
        }

        num_extenso = ["Zero","Um","Dois","Tres","Quatro","Cinco"]
        number = 1

        lstProdutos = list(mvx_cliente.produtos)
        lstProdutos.sort(key= lambda p : datetime.strptime(p.data, "%d/%m/%Y %H:%M:%S"),reverse=True)
        if len(lstProdutos) > 5:
            lstProdutos = lstProdutos[:5]
        for produto in lstProdutos:
            chaves = [f"Produto_{num_extenso[number]}",
                      f"DataProduto_{num_extenso[number]}",
                      f"Categoria_{num_extenso[number]}",
                      f"Departamento_{num_extenso[number]}",
                      f"Loja_{num_extenso[number]}",
                      f"Canal_{num_extenso[number]}",
                      f"ProdutoMvxCod_{num_extenso[number]}"]
            campos.update({
                chaves[0]: produto.nome,
                chaves[1]: produto.data,
                chaves[2]: produto.desc_linha,
                chaves[3]: produto.desc_setor,
                chaves[4]: produto.empresa.nome,
                chaves[5]: produto.canal,
                chaves[6]: produto.cod_produto,
            })
            number += 1
        
        campos_formatado = list(map(lambda x: campo_esqueleto.format(x,campos[x]), campos.keys()))
        return "|||".join(campos_formatado)

    def montar_cliente(self, emblue_data, email_id):
        cliente = Cliente(None)
        cliente.nome_cliente = get_field(emblue_data, 'nombre')
        cliente.cnpj = get_field(emblue_data, 'CNPJ')
        cliente.doc_cliente = get_field(emblue_data, 'CPF')
        cliente.sexo = get_field(emblue_data, 'sexo')
        cliente.email_cliente = ''
        cliente.cel_cliente = get_field(emblue_data, 'telefono_1')
        cliente.data_nascimento = get_field(emblue_data, 'cumpleanios')
        cliente.cidade_cliente = get_field(emblue_data, 'ciudad')
        cliente.uf_cliente = get_field(emblue_data, 'Estado')
        cliente.pais = encontrar_cod(get_field(emblue_data, 'pais'))
        cliente.tipo = 'c'
        cliente.produtos = list()
        cliente.emblue_email_id = email_id
        cliente.novos_produtos_qtd = 0

        p5 = ProdutoVendido(None,None,None)
        p5.cod_produto = get_field(emblue_data, 'ProdutoMvxCod_Cinco')
        p5.nome = get_field(emblue_data, 'Produto_Cinco')
        p5.desc_setor = get_field(emblue_data, 'Departamento_Cinco')
        p5.desc_linha = get_field(emblue_data, 'Categoria_Cinco')
        p5.data = get_field(emblue_data, 'DataProduto_Cinco')
        p5.empresa = Empresa(None)
        p5.empresa.nome = get_field(emblue_data, 'Loja_Cinco')
        p5.canal = get_field(emblue_data, 'Canal_Cinco')
        cliente.produtos.append(p5)


        p4 = ProdutoVendido(None,None,None)
        p4.cod_produto = get_field(emblue_data, 'ProdutoMvxCod_Quatro')
        p4.nome = get_field(emblue_data, 'Produto_Quatro')
        p4.desc_setor = get_field(emblue_data, 'Departamento_Quatro')
        p4.desc_linha = get_field(emblue_data, 'Categoria_Quatro')
        p4.data = get_field(emblue_data, 'DataProduto_Quatro')
        p4.empresa = Empresa(None)
        p4.empresa.nome = get_field(emblue_data, 'Loja_Quatro')
        p4.canal = get_field(emblue_data, 'Canal_Quatro')
        cliente.produtos.append(p4)


        p3 = ProdutoVendido(None,None,None)
        p3.cod_produto = get_field(emblue_data, 'ProdutoMvxCod_Tres')
        p3.nome = get_field(emblue_data, 'Produto_Tres')
        p3.desc_setor = get_field(emblue_data, 'Departamento_Tres')
        p3.desc_linha = get_field(emblue_data, 'Categoria_Tres')
        p3.data = get_field(emblue_data, 'DataProduto_Tres')
        p3.empresa = Empresa(None)
        p3.empresa.nome = get_field(emblue_data, 'Loja_Tres')
        p3.canal = get_field(emblue_data, 'Canal_Tres')
        cliente.produtos.append(p3)

        
        p2 = ProdutoVendido(None,None,None)
        p2.cod_produto = get_field(emblue_data, 'ProdutoMvxCod_Dois')
        p2.nome = get_field(emblue_data, 'Produto_Dois')
        p2.desc_setor = get_field(emblue_data, 'Departamento_Dois')
        p2.desc_linha = get_field(emblue_data, 'Categoria_Dois')
        p2.data = get_field(emblue_data, 'DataProduto_Dois')
        p2.empresa = Empresa(None)
        p2.empresa.nome = get_field(emblue_data, 'Loja_Dois')
        p2.canal = get_field(emblue_data, 'Canal_Dois')
        cliente.produtos.append(p2)

        p1 = ProdutoVendido(None,None,None)
        p1.cod_produto = get_field(emblue_data, 'ProdutoMvxCod_Um')
        p1.nome = get_field(emblue_data, 'Produto_Um')
        p1.desc_setor = get_field(emblue_data, 'Departamento_Um')
        p1.desc_linha = get_field(emblue_data, 'Categoria_Um')
        p1.data = get_field(emblue_data, 'DataProduto_Um')
        p1.empresa = Empresa(None)
        p1.empresa.nome = get_field(emblue_data, 'Loja_Um')
        p1.canal = get_field(emblue_data, 'Canal_U')
        cliente.produtos.append(p1)

        return cliente


def get_field(array_emblue,name):
    field = next(filter(lambda x: x['nombre'] == name,array_emblue), None)
    if(field is None):
        return ''
    return field['valor']

