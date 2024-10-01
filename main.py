

from mvx.mvx_service import *
from shared.log import *
from classes import *
from itertools import groupby
from emblue.emblue_service import *
from store import *
from falhaService import *
import traceback
from shared.credenciais import *
import logging
import time
import schedule


def startup():
    init_log()

    data_i = datetime.today() - timedelta(days=1)
    data_f = datetime.today() - timedelta(seconds=1)
    
    run(data_i,data_f)


def run(data_i,data_f):

    tentativas = 2

    while tentativas > 0:
        if tentativas != 3:
            log(f"Tentativa de extracao numero: {str(2-tentativas)}")

        try:
            
            extracao = ExtracaoDiaria(data_i, data_f)

            extracao.criar_serviço_emblue()

            if extracao.validar_emblue() is False:
                raise "Falha na emblue"

            if extracao.carregar_empresas() is False:
                raise "Falha para carregar empresas"
            
            if extracao.carregar_movimentos() is False:
                raise "Falha ao buscar os movimentos"

            extracao.processar_movimentos()

            if extracao.validar_emblue() is False:
                raise "Falha na emblue"
            
            if extracao.integrar_emblue(False) is False:
               raise "Falha para integrar na emblue"

            extracao.finalizar()

            return
            

        except Exception as e:
            log("Excecao MAIN")
            log(str(e))
            logging.exception("message")
            time.sleep(60)

        finally:
            tentativas -= 1


class ExtracaoDiaria:

    def __init__(self, data_i, data_f) -> None:

        self.data_i = data_i
        self.data_f = data_f

        #Serviço para realizar consultas na Microvix
        self.mvx_service = MvxService()

        self.falha_service = FalhaService()
        
        #Serviço para integrar os usuário na emblue
        #self.criar_serviço_emblue()

        #Repositório temporario em memoria de movimentações de clientes
        self.mov_temp_repo = TempClienteMovimentoService()
        #Repositório temporario em memoria de clientes
        self.c_repo = TempClientesService()
        #Repositório em arquivo de clientes não tipo C (lightweight)
        self.c_bl_repo = BlacklistClienteService("data/clientes_bl.txt")
        #Repositorio em arquivo de identificação do cliente (lightweight)
        self.c_id_repo = ClienteIdService("data/mvx_vs_emblue.txt")
        
        #Quando Falso mesmo os clientes não alterados são integrados na emblue
        self.integrar_somente_clientes_alterados = True

        #Todas as empresas
        self.empresas = list()
        self.contagem_de_empresas = 0
        self.contagem_empresa_itr = 0
        self.contagem_empresa_suc = 0
        self.contagem_empresa_err = 0

        pass


    def criar_serviço_emblue(self):
        credenciais = carregar_credenciais()
        self.emb_service = EmblueService(credenciais['emblue_token'],credenciais['emblue_usuario'],credenciais['emblue_senha'])
        log("Servico da Emblue Criado")
        

    def validar_emblue(self) -> bool:
        log("Validando emblue")
        resposta_do_token = self.emb_service.token_res
        if isinstance(resposta_do_token, str):
            log("Erro com o token da emblue")
            log(resposta_do_token)
            return False
        log("Servico da Emblue Validado: OK!")
        return True


    def carregar_empresas(self) -> bool:
        #Busca todas as empresas
        mvx_empresas = self.mvx_service.empresas()
        if isinstance(mvx_empresas,str):
            log("falha para buscar as empresas")
            log(mvx_empresas)
            return False
        
        mvx_empresas_com_cnpj = list(filter(lambda x: len(x["CNPJ"])>0, mvx_empresas))
        mvx_grupo_cnpj = groupby(mvx_empresas_com_cnpj,lambda x: x["CNPJ"])

        for cnpj, lista in mvx_grupo_cnpj:
            empresa = Empresa(list(lista).pop())
            self.empresas.append(empresa)
        
        self.contagem_de_empresas = len(self.empresas)
        log(f"Empresas carregadas. Total de {self.contagem_de_empresas} empresas")
        return True
    

    def carregar_movimentos(self) -> bool:

        log(f"Extraindo movimentos de {datetime.strftime(self.data_i, "%d/%m/%Y %H:%M:%S")} ate {datetime.strftime(self.data_f, "%d/%m/%Y %H:%M:%S")}")

        # busca movimentos de cnpj
        for empresa in self.empresas:
            cnpj = empresa.cnpj

            log("Consultando a empresa: "+ cnpj)
            mvx_movimentos = self.mvx_service.movimentos(cnpj,self.data_i,self.data_f)
            self.contagem_empresa_itr += 1
            
            if isinstance(mvx_movimentos,str):
                log(f"Não foi possivel buscar os movimentos da empresa {cnpj} ")
                log(mvx_movimentos)

                self.contagem_empresa_err += 1

                self.falha_service.addEmpresa(cnpj,self.data_i,self.data_f)

                if self.contagem_empresa_err >= 15:
                    log("Processo Abortado: Houve mais de 15 falhas para buscar os movimentos das empresas")
                    return False
                continue

            self.contagem_empresa_suc += 1
            
            for mvx_mov in mvx_movimentos:
                self.mov_temp_repo.add(mvx_mov['codigo_cliente'],mvx_mov)

            log(f"Consultas {str(self.contagem_empresa_itr)} / {str(self.contagem_de_empresas)} | Successo: {self.contagem_empresa_suc} - Falhas: {self.contagem_empresa_err}")
            
            ##if self.contagem_empresa_suc > 15: ##TODO: Remover
            #    break

        return True


    def resolver_cliente(self, cod_cliente, cnpj) -> Cliente:
        #Esta na blacklist?
        if self.c_bl_repo.encontrar(cod_cliente) is not None:
            return None

        #Esta em memoria?
        cliente = self.c_repo.encontrar(cod_cliente)
        if cliente is None:
            #Encontra na MVX
            cliente = self.mvx_service.encontrar_cliente(cnpj,cod_cliente)
            if isinstance(cliente,  str):
                log(f"Cliente {cod_cliente} não encontrado para cnpj {cnpj}. Erro:")
                log(cliente)
                return None

            #Após primeira consulta: verificar se não é cliente e colocar na blacklist
            if cliente.tipo.lower() != 'c':
                self.c_bl_repo.add(cod_cliente)
                return None

            #Encontre o id da emblue
            (emblue_id, email) = self.c_id_repo.encontrar(cod_cliente)

            # Verifica Emblue
            if emblue_id is None:
                #Procurar na emblue
                resultado = self.emb_service.api.existe_contato(cliente.email_cliente)
                if isinstance(resultado,  str):
                    log(f"Falha ao buscar o usuario {cliente.email_cliente} na emblue. cod: {cod_cliente}")
                    log(resultado)
                    return None

                emblue_id = resultado

            #atualiza o id no cliente
            cliente.emblue_email_id = emblue_id

            if emblue_id == -1:
                log(f"O usuario não existe na emblue. cod: {cod_cliente} ")
            else:
                emblueCliente = self.emb_service.api.buscar_cliente(emblue_id)
                if isinstance(emblueCliente,str):
                    log(f"Falha para trazer o usuario da emblue {emblue_id}. cod: {cod_cliente} ")
                    log(emblueCliente)
                    return None

                cliente.produtos = list(filter(lambda p : p.cod_produto != '' and p.data != '', emblueCliente.produtos))

            self.c_repo.add(cliente)

        return cliente


    def processar_movimentos(self):
        log("Iniciando processamento dos movimentos")
        codcliente_movimentos_dict = self.mov_temp_repo.cliente_mov_dic
        for cod_cliente, mvx_movs in codcliente_movimentos_dict.items():
            cnpj = mvx_movs[0]['cnpj_emp']

            cliente = self.resolver_cliente(cod_cliente,cnpj)
            if cliente == None:
                continue

            movs_c_data = list(filter(lambda mov : mov['dt_update'] != '',mvx_movs))
            ordenado_mvx_movs = sorted(movs_c_data, key=lambda mov: datetime.strptime(mov['dt_update'],"%d/%m/%Y %H:%M:%S"))
            mvx_mov_top5 = ordenado_mvx_movs[-5:] if len(ordenado_mvx_movs) >=5 else ordenado_mvx_movs

            for mov5 in mvx_mov_top5:
                data = mov5['dt_update']
                dataTipada = datetime.strptime(data,"%d/%m/%Y %H:%M:%S")
                if cliente.devo_adicionar_produto(dataTipada) is False:
                    break
                else:
                    cnpj = mov5['cnpj_emp']
                    cod_produto = mov5['cod_produto']
                    mvx_produto = self.mvx_service.encontrar_produto(cnpj,cod_produto)
                    if(isinstance(mvx_produto,str)):
                        log(f"Falha para buscar o produto {cod_produto}")
                        log(mvx_produto)
                    else:
                        empresa = next(filter(lambda x: x.cnpj == cnpj,self.empresas))
                        produto = ProdutoVendido(mvx_produto,empresa,data)
                        cliente.add_produto(produto)

            log(f"Requisicoes na MVX ate aqui. Clientes: {str(self.mvx_service.contagem_req_clientes)} | Produtos: {str(self.mvx_service.contagem_req_produtos)}")


    def integrar_emblue(self, local) -> bool:
        log("Integrando na emblue")
        clientes = list(
            filter(
                lambda x: len(x.email_cliente) > 0 
                    and (self.integrar_somente_clientes_alterados is False or x.novos_produtos_qtd > 0) 
                    and x.tipo == 'c', 
                self.c_repo.clientes))
        
        if local is True:
            log("Modo debug ativado: Salvando em arquivo")
            with open("_logs/clientes_temp.txt", 'w') as file:
                for c in clientes:
                    file.write(c.to_json())
            return
        
        contagem_clientes = len(clientes)
        contagem_itr = 0
        contagem_suc = 0
        contagem_err = 0

        for cliente in clientes:
            resultado = self.emb_service.atualizar_contato(cliente)
            contagem_itr += 1
            if resultado == True:
                contagem_suc += 1
                log(f'Usuarios integrados na emblue: {contagem_suc}/{contagem_clientes} | Total de Falhas: {contagem_err} | Usuario atual {cliente.emblue_email_id}')
                self.c_id_repo.add(cliente.cod_cliente,cliente.emblue_email_id, cliente.email_cliente)
            else:
                contagem_err += 1
                log(f'Falha de integracao na emblue. Cod: {cliente.cod_cliente}. EmblueId: {cliente.emblue_email_id}. Email: {cliente.email_cliente}')
                self.falha_service.addCliente(cliente.cod_cliente,self.data_i,self.data_f,"emblue")
                if contagem_err >= 20:
                    log("Processo Abortad: Houve mais de 20 falhas para integrar o usuários na emblue")
                    return False
        return True


    def finalizar(self):
        self.c_bl_repo.salvar()
        self.c_id_repo.salvar()
        log(f'Processo finalizado')


if __name__ == "__main__":

    debug = True

    if debug:
        data_i = datetime.strptime("16/08/2024 00:00:00", "%d/%m/%Y %H:%M:%S")
        data_f = datetime.strptime("18/08/2024 23:59:59", "%d/%m/%Y %H:%M:%S")
        run(data_i,data_f)
    else:
        schedule.every().day.at('06:00').do(startup)
        while True:
            schedule.run_pending()
            min10 = 600000
            time.sleep(min10)