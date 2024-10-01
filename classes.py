
from datetime import datetime, timedelta
import json

class Empresa:
    def __init__(self, mvxEmpresa):
        self.cnpj = mvxEmpresa['CNPJ'] if mvxEmpresa != None else ''
        self.nome = mvxEmpresa['nome_portal'] if mvxEmpresa != None else ''


class ProdutoVendido:
    def __init__(self,mvxproduto, empresa, dataCompra):
        self.cod_produto = mvxproduto['cod_produto'] if mvxproduto != None else ''
        self.nome = mvxproduto['nome'] if mvxproduto != None else ''
        self.desc_linha = mvxproduto['desc_linha'] if mvxproduto != None else ''
        self.desc_setor = mvxproduto['desc_setor'] if mvxproduto != None else ''
        self.data = dataCompra if dataCompra != None else ''
        self.canal = ('Virtual' if mvxproduto['loja_virtual'] == 'S' else 'Fisica') if mvxproduto != None else ''
        self.empresa = empresa


class Cliente:

    QTD_PRODUTO_LIMITE = 5

    def __init__(self, mvxcliente):
        self.cod_cliente = mvxcliente['cod_cliente'] if mvxcliente != None else ''
        self.nome_cliente = mvxcliente['nome_cliente'] if mvxcliente != None else ''
        self.razao_cliente = mvxcliente['razao_cliente'] if mvxcliente != None else ''
        self.cnpj = mvxcliente['doc_cliente'] if mvxcliente != None and mvxcliente['tipo_cliente'] == 'J' else ''
        self.doc_cliente = mvxcliente['doc_cliente'] if mvxcliente != None and mvxcliente['tipo_cliente'] != 'J' else ''
        self.sexo = mvxcliente['sexo'] if mvxcliente != None else ''
        self.email_cliente = mvxcliente['email_cliente'] if mvxcliente != None else ''
        self.cel_cliente = mvxcliente['cel_cliente'] if mvxcliente != None else ''
        self.data_nascimento = mvxcliente['data_nascimento'] if mvxcliente != None else ''
        self.cidade_cliente = mvxcliente['cidade_cliente'] if mvxcliente != None else ''
        self.uf_cliente = mvxcliente['uf_cliente'] if mvxcliente != None else ''
        self.pais = mvxcliente['pais'] if mvxcliente != None else ''
        self.tipo = mvxcliente['tipo_cadastro'].lower() if mvxcliente != None else ''
        self.produtos = []
        self.emblue_email_id = 0
        self.novos_produtos_qtd = 0


    def devo_adicionar_produto(self, dataTipada):
        
        if len(self.produtos) < self.QTD_PRODUTO_LIMITE:
            return True
        self.produtos.sort(key= lambda p : datetime.strptime(p.data, "%d/%m/%Y %H:%M:%S"),reverse=True)
        return datetime.strptime(self.produtos[0].data, "%d/%m/%Y %H:%M:%S") < dataTipada

    def add_produto(self, produtoVendido):
        if produtoVendido.cod_produto in list(map(lambda x: x.cod_produto,self.produtos)):
            return False
        
        self.produtos.append(produtoVendido)
        self.produtos.sort(key= lambda p : datetime.strptime(p.data, "%d/%m/%Y %H:%M:%S"), reverse=True)
        if len(self.produtos) > self.QTD_PRODUTO_LIMITE:
            self.produtos = self.produtos[:self.QTD_PRODUTO_LIMITE]
            
        self.novos_produtos_qtd += 1

    def to_json(self):
        thisDic = self.__dict__.copy()

        dictProdutos = [p.__dict__ for p in self.produtos]
        for p in dictProdutos:
            if p['empresa'] != None:
                p['empresa'] = p['empresa'].__dict__.copy()

        thisDic.update({ 'produtos': dictProdutos})
        return json.dumps(thisDic)
    
    def qtd_produtos_atuais(self,quantidade):
        dataDeCorte = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        prods = list(filter(lambda p: datetime.strptime(p.data, "%d/%m/%Y %H:%M:%S") >= dataDeCorte,self.produtos))
        return len(prods) >= quantidade
    
    def mantem_ultimos_produtos(self,qtd):
        self.produtos = self.produtos[qtd:]
