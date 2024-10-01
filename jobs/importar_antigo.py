

from mvx.mvx_service import *
from shared.log import *
from classes import *
from itertools import groupby
from emblue.emblue_service import *
import time

service = MvxService()

skipTouched = False

#busca todas as empresas
empresaLst = service.empresas()
if isinstance(empresaLst,str):
    log("falha para buscar as empresas")
    log(empresaLst)
    quit()


# filtra empresas por:
# 1. Tem CNPJ
# 2. CNPJ Distinto
empresasComCnjp = list(filter(lambda x: len(x["CNPJ"])>0, empresaLst))
empresasPorCnpj = groupby(empresasComCnjp,lambda x: x["CNPJ"])
empresasFiltradas = []
for key, group in empresasPorCnpj:
    empresasFiltradas.append(list(group).pop())

# busca lojas de cada empresa
mvx_empresa_lojas_lst = list()
mvx_emp_ls_temp = None

for empresa in empresasFiltradas:
    cnpj = empresa['CNPJ']
    mvx_emp_ls_temp = Empresa(empresa)
    mvx_empresa_lojas_lst.append(mvx_emp_ls_temp)
    # lojas_lst = service.lojas(cnpj)

    # if isinstance(lojas_lst, str):
    #     log("Falha para buscar a loja do cnpj" + cnpj)
    #     log(lojas_lst)
    # elif len(lojas_lst) > 0:
    #     for l in lojas_lst:
    #         mvx_emp_ls_temp.addLoja(l)
    #     mvx_empresa_lojas_lst.append(mvx_emp_ls_temp)



# busca movimentos de cnpj
total_empresas = len(mvx_empresa_lojas_lst)
contagem_empresas_consultadas = 0
for mvx_emp_lojas in mvx_empresa_lojas_lst:
    cnpj = mvx_emp_lojas.cnpj

    log("Consultando a empresa: "+ cnpj)
    
    dates = [
        [datetime.strptime('2024-05-01', '%Y-%m-%d'), datetime.strptime('2024-06-10', '%Y-%m-%d')],
        [datetime.strptime('2024-03-01', '%Y-%m-%d'), datetime.strptime('2024-05-01', '%Y-%m-%d')],
        [datetime.strptime('2024-01-01', '%Y-%m-%d'), datetime.strptime('2024-03-01', '%Y-%m-%d')],

        [datetime.strptime('2023-11-01', '%Y-%m-%d'), datetime.strptime('2024-01-01', '%Y-%m-%d')],
        [datetime.strptime('2023-09-01', '%Y-%m-%d'), datetime.strptime('2023-11-01', '%Y-%m-%d')],
        [datetime.strptime('2023-07-01', '%Y-%m-%d'), datetime.strptime('2023-09-01', '%Y-%m-%d')],
        [datetime.strptime('2023-05-01', '%Y-%m-%d'), datetime.strptime('2023-07-01', '%Y-%m-%d')],
        [datetime.strptime('2023-03-01', '%Y-%m-%d'), datetime.strptime('2023-05-01', '%Y-%m-%d')],
        [datetime.strptime('2023-01-01', '%Y-%m-%d'), datetime.strptime('2023-03-01', '%Y-%m-%d')],

        [datetime.strptime('2022-11-01', '%Y-%m-%d'), datetime.strptime('2023-01-01', '%Y-%m-%d')],
        [datetime.strptime('2022-09-01', '%Y-%m-%d'), datetime.strptime('2022-11-01', '%Y-%m-%d')],
        [datetime.strptime('2022-07-01', '%Y-%m-%d'), datetime.strptime('2022-09-01', '%Y-%m-%d')],
        [datetime.strptime('2022-05-01', '%Y-%m-%d'), datetime.strptime('2022-07-01', '%Y-%m-%d')],
        [datetime.strptime('2022-03-01', '%Y-%m-%d'), datetime.strptime('2022-05-01', '%Y-%m-%d')],
        [datetime.strptime('2022-01-01', '%Y-%m-%d'), datetime.strptime('2022-03-01', '%Y-%m-%d')],
    ]

    for dts in dates:
        
        log("Periodo: "+ dts[0].strftime("%Y-%m-%d %H:%M:%S") + " ate " + dts[1].strftime("%Y-%m-%d %H:%M:%S") )
        movs = service.movimentos(cnpj,dts[0],dts[1])
        if isinstance(movs,str):
            log(f"Não foi possivel buscar os movimentos da empresa {cnpj} ")
            log(movs)
            continue
        
        for mov in movs:

            mvxCliente = service.encontrar_cliente(cnpj,mov['codigo_cliente'])
            if(isinstance(mvxCliente,str)):
                log(mvxCliente)
            elif mvxCliente.tipo == 'c':

                #Se os ultimos 5 produtos do cliente for de hoje, então desconsidera movimentação
                if mvxCliente.qtd_produtos_atuais(5) is True:
                    continue

                produto = service.encontrar_produto(cnpj,mov['cod_produto'])
                if(isinstance(produto,str)):
                    log(produto)
                else:
                    mvx_produto = ProdutoVendido(produto,mvx_emp_lojas.empresa,mov['dt_update'])
                    mvxCliente.addProduto(mvx_produto)

            #time.sleep(0.2)
        
        contagem_empresas_consultadas += 1
        log("Consultas " + str(contagem_empresas_consultadas) + '/' + str(total_empresas))
        log("Requisicoes ate aqui. Clientes:" + str(service.contagem_req_clientes) + ' | Produtos:' + str(service.contagem_req_produtos))
        service.salvar_em_memoria()
    


#filtra clientes para atualizar:
mvx_clientes = list(filter(lambda x: len(x.email_cliente) > 0 and (skipTouched or x.touched) and x.tipo == 'c', service.LISTA_MVXCLIENTES)) #
usuarios_integrados = 0
usuarios_nao_integrados = 0
emblue = EmblueService("R08FuPOT-FUpQV-2HYbH-utu69rLiHQ","emblue.mundoverde@hagaze.com.br","aT.q86zMhgR2eFF@")
if isinstance(emblue.token_res, str):
    log(emblue.token_res)
    quit()
else:
    for mvx_cliente in mvx_clientes:
        res = emblue.atualizar_contato(mvx_cliente)
        if res == True:
            usuarios_integrados += 1
            log(f'Usuarios integrados na emblue: {usuarios_integrados}/{len(mvx_clientes)}')
        else:
            usuarios_nao_integrados += 1
            log(f'Falha de integração na emblue: {usuarios_nao_integrados}')
        time.sleep(0.2)

    service.salvar_em_memoria()




