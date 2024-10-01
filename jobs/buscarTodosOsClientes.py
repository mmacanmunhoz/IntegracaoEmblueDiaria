from mvx.mvx_service import *
from shared.log import *
from itertools import groupby

service = MvxService()
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

contagem = 0
itr = 0
emps = len(empresasFiltradas)
for empresa in empresasFiltradas:
    cnpj = empresa['CNPJ']

    creal,qtd = service.buscar_todos_os_clientes(cnpj, '2022-01-01', '2022-06-01')
    itr += 1
    if isinstance(qtd, str):
        log(f"Falha para carregar os clientes do cnpj: {cnpj} - {qtd}")
    else:
        contagem += creal
        log(f"[{itr}/{emps}] Clientes extraidos {cnpj}: +{creal} / {qtd} | {contagem}")

service.salvar_em_memoria()