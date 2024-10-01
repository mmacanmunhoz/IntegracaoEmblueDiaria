
from mvx.mvx_service import *
import csv

service = MvxService()

clientes = list(filter(lambda x: x.tipo == 'c' and len(x.email_cliente) > 0,service.LISTA_MVXCLIENTES))

with open('clientes_export.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(['email','cpf','nome','codigo','telefone','nascimento','cidade','uf','pais','tipo',
                     'Produto 1 Nome','Produto 1 Departamento', 'Produto 1 Categoria', 'Produto 1 Data', 'Produto 1 Canal', 'Produto 1 Cnpj',
                     'Produto 2 Nome','Produto 2 Departamento', 'Produto 2 Categoria', 'Produto 2 Data', 'Produto 2 Canal', 'Produto 2 Cnpj',
                     'Produto 3 Nome','Produto 3 Departamento', 'Produto 3 Categoria', 'Produto 3 Data', 'Produto 3 Canal', 'Produto 3 Cnpj',
                     'Produto 4 Nome','Produto 4 Departamento', 'Produto 4 Categoria', 'Produto 4 Data', 'Produto 4 Canal', 'Produto 4 Cnpj',
                     'Produto 5 Nome','Produto 5 Departamento', 'Produto 5 Categoria', 'Produto 5 Data', 'Produto 5 Canal', 'Produto 5 Cnpj'])
    for c in clientes:
        vals = list([c.email_cliente,c.doc_cliente,c.nome_cliente,c.cod_cliente,c.cel_cliente, c.data_nascimento, c.cidade_cliente, c.uf_cliente, c.pais, c.tipo])
        produtos = list(c.produtos)
        produtos.reverse()
        for p in produtos:
            vals.append(p.nome)
            vals.append(p.desc_setor)
            vals.append(p.desc_linha)
            vals.append(p.data)
            vals.append(p.canal)
            vals.append(p.cnpj)

        # Write the data
        writer.writerow(vals)