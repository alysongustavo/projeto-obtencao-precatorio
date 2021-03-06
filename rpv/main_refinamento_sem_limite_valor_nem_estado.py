# consulta os dados do site http://rpvprecatorio.trf5.jus.br/

import aiohttp
import asyncio
import locale

from aiohttp import ClientSession
from pip._vendor.urllib3.exceptions import HTTPError

TRF5_URL="http://www4.trf5.jus.br/cp/cp.do"

filePrecatorio = open("../dados/2018/rpv/resultados/rpv_cancelados.txt", 'r')
Lines = filePrecatorio.readlines()

# Cria um array para popular os dados do arquivo
LISTA_RPV = []

# Popula o arquivo com os dados do arquivo
for line in Lines:
   LISTA_RPV.append(line.strip())

def formatarValor(str_valor):
    indexVirgula = str_valor.index(',')
    tamanhoPalavra = len(str_valor)
    novo_caracter = ''

    valorFormatado = str_valor[:indexVirgula] + novo_caracter + str_valor[indexVirgula + tamanhoPalavra:]
    return valorFormatado


def escrever_file_precatorio_cancelado_refinado(valorDepositado, cpf, nome, estado, local, rpv):
    f = open(
        '../resultados/2018/rpv/rpv_informacoes.txt', 'a')
    g = open(
        '../resultados/2018/rpv/rpv_informacoes.csv', 'a')

    g.write(str(nome) + '|' + str(cpf) + '|' + str(estado) + '|' + str(local) + '|' + str(valorDepositado) + '|' + str(rpv) + '\n')
    g.close()

    f.write(rpv + '\n')
    f.close()

def escrever_file_falha_request(rpv):
    f = open('../resultados/2018/rpv/arquivo_falha_request.txt', 'a')
    f.write(rpv + '\n')
    f.close()

def ler_file_total_precatorio():
    LISTA_RPV_LIMPOS = []
    filePrecatorio = open("../dados/2018/rpv/resultados/rpv_cancelados.txt", 'r')
    Lines = filePrecatorio.readlines()
    for line in Lines:
        LISTA_RPV_LIMPOS.append(line.strip())

    filePrecatorio.close()
    return LISTA_RPV_LIMPOS

def ler_file_precatorio_cancelado_refinado():
   LISTA_RPV_CANCELADO =[]
   filePrecatorio = open(
       "../dados/2018/rpv/resultados/todos_estados_quaisquer_valores/precatorios_cancelados_todos_estados_qualquer_valor_somente_rpv.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_RPV_CANCELADO.append(line.strip())

   filePrecatorio.close()
   return LISTA_RPV_CANCELADO

def ler_arquivo_falha_request():
   LISTA_RPV_FALHA_REQUEST =[]
   filePrecatorio = open("../dados/2018/rpv/resultados/todos_estados_quaisquer_valores/arquivo_falha_request.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_RPV_FALHA_REQUEST.append(line.strip())

   filePrecatorio.close()
   return LISTA_RPV_FALHA_REQUEST

async def make_account():
    url = TRF5_URL
    f = open('../dados/2018/rpv/resultados/todos_estados_quaisquer_valores/arquivo_falha_request.txt', 'w')
    f.close()

    async with aiohttp.ClientSession() as session:
        post_tasks = []
        # now execute them all at once
        await asyncio.gather(*[do_post(session, url, rpv) for rpv in LISTA_RPV])

async def do_post(session, url, rpv):

    try:

        if (rpv in ler_file_precatorio_cancelado_refinado()):
            print(f"O RPV {rpv} ja esta em um dos arquivos cancelados ou o outro")
        else:
            async with session.post(url, data ={
                "tipo": "xmlrpvprec",
                "filtroRPV_Precatorios": rpv,
                "tipoproc": "R",
                "ordenacao": "p"
                    }) as response: data = await response.text()

            # Obten????o do Valor Depositado
            startValorDepositado = 'Dep&iuml;&iquest;&iquest;sito: R$ '
            endValorDepositado = ','
            valorDepositadoFiltrado = data.split(startValorDepositado)[1].split(endValorDepositado)[0]

            # Obten????o do RPV
            startRPV = '="14%">RPV'
            endRPV = '-'
            rpvFiltrado = data.split(startRPV)[1].split(endRPV)[0]

            # Obten????o do Estado
            startEstado = '="14%">RPV' + rpv + '-'
            endEstado = '</td>'
            estadoFiltrado = data.split(startEstado)[1].split(endEstado)[0]

            startLocal = 'JU&Iacute;ZO DA '
            endLocal = '</td>'
            localFiltrado = data.split(startLocal)[1].split(endLocal)[0]

            startDoc = 'Documento: '
            endDoc = ','
            documentoFiltrado = data.split(startDoc)[1].split(endDoc)[0]

            startBeneficiario = 'Beneficiario: '
            endBeneficiario = ','
            beneficiarioFiltrado = data.split(startBeneficiario)[1].split(endBeneficiario)[0]

            if (rpvFiltrado in ler_file_precatorio_cancelado_refinado()):
                print(f"RPV: {rpv} j?? esta no arquivo de precatorio cancelado refinado")
            elif (rpvFiltrado == rpv):
                escrever_file_precatorio_cancelado_refinado(valorDepositadoFiltrado, documentoFiltrado, beneficiarioFiltrado, estadoFiltrado, localFiltrado , rpvFiltrado)

    except HTTPError as aiohttp:

        if(rpv in ler_file_precatorio_cancelado_refinado()):
            print(f"O RPV {rpv} ja esta em um dos arquivos de precatorio refinado na exception {aiohttp}")
        else:
            escrever_file_falha_request(rpv)

        print(f"Ocorreu um erro no HTTPError {aiohttp}")
    except Exception as err:
        if(rpv in ler_arquivo_falha_request() or rpv in ler_file_precatorio_cancelado_refinado()):
            print(f"O RPV {rpv} j?? est?? gravado no arquivo de requi????es falhadas refinados")
        else:
            escrever_file_falha_request(rpv)

        print(f"Ocorreu um erro no Exception Generico {err}")
    finally:
        print("Resumo do processamento!")

        lista_total_precatorios = ler_file_total_precatorio()
        lista_precatorios_cancelados = ler_file_precatorio_cancelado_refinado()
        lista_precatorios_falha_request = ler_arquivo_falha_request()

        print(f"Quantidade total precatorio cancelados: {len(lista_total_precatorios)} ")
        print(f"Quantidade precatorios cancelados refinados: {len(lista_precatorios_cancelados)}")
        print(f"Quantidade precatorios falha request: {len(lista_precatorios_falha_request)}")

        print("Conclus??o do processamento!")

        if(len(lista_total_precatorios) == len(lista_precatorios_cancelados)):
            print("Todo os precatorios foram analisados com sucesso!")
        else:
            print(f"Ainda falta {(len(lista_total_precatorios) - (len(lista_precatorios_cancelados)  + len(lista_precatorios_falha_request)))} serem processados!")

def main():
   loop = asyncio.get_event_loop()
   loop.run_until_complete(make_account())
   loop.close()

main()