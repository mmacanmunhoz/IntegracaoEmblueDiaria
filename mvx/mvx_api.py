
from mvx.mvx_util import mvx_req_xml, mvx_montar_corpo_req, MVX_CHAVE



# Consulta a api da Microvix para empresas
def buscar_empresas():
  params = [ 
    { 'id':'Chave', 'value': MVX_CHAVE}
  ]
  xml = mvx_montar_corpo_req("LinxGrupoLojas", params)

  return mvx_req_xml(xml)

# Consulta a api da Microvix para buscar as lojas
def buscar_lojas(cnpj):
  params = [ 
    { 'id':'chave', 'value': MVX_CHAVE},
    { 'id':'cnpjEmp', 'value': cnpj} 
  ]
  return mvx_req_xml(mvx_montar_corpo_req("LinxLojas", params))

# Consulta a api da Microvix para os movimentos de uma empresa
def buscar_movimentos(cnpj,data_ini, data_fin):
  params = [ 
    { 'id':'chave', 'value': MVX_CHAVE},
    { 'id':'cnpjEmp', 'value': cnpj},
    { 'id':'data_inicial', 'value': data_ini.strftime("%Y-%m-%d %H:%M:%S")},
    { 'id':'data_fim', 'value': data_fin.strftime("%Y-%m-%d %H:%M:%S")} 
  ]
  return mvx_req_xml(mvx_montar_corpo_req("LinxMovimento", params))

# Consulta a api da Microvix para buscar o cliente
def buscar_cliente(cnpj,cod_cliente):
  params = [ 
    { 'id':'chave', 'value': MVX_CHAVE},
    { 'id':'cnpjEmp', 'value': cnpj},
    { 'id':'cod_cliente', 'value': cod_cliente},
    { 'id':'data_inicial', 'value': 'NULL'},
    { 'id':'data_fim', 'value': 'NULL'} 
  ]

  return mvx_req_xml(mvx_montar_corpo_req("LinxClientesFornec", params))

# Consulta a api da Microvix para buscar todos os cliente
def buscar_todos_os_cliente(cnpj, data_i, data_f):
  params = [ 
    { 'id':'chave', 'value': MVX_CHAVE},
    { 'id':'cnpjEmp', 'value': cnpj},
    { 'id':'data_inicial', 'value': data_i},
    { 'id':'data_fim', 'value': data_f} ,
    { 'id':'tipo_cadastro', 'value': 'C'} 
  ]

  return mvx_req_xml(mvx_montar_corpo_req("LinxClientesFornec", params))

# Consulta a api da Microvix para buscar o produto
def buscar_produto(cnpj,cod):
  params = [ 
    { 'id':'chave', 'value': MVX_CHAVE},
    { 'id':'cnpjEmp', 'value': cnpj},
    { 'id':'cod_produto', 'value': cod},
    { 'id':'dt_update_inicio', 'value': 'NULL'},
    { 'id':'dt_update_fim', 'value': 'NULL'} 
  ]

  return mvx_req_xml(mvx_montar_corpo_req("LinxProdutos", params))