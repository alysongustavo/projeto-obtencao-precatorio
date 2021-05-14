#importando tabelas em pdf usando o pytabula

# import tabula
# import requests
import aiohttp
import asyncio
import locale



from aiohttp import ClientSession
from pip._vendor.urllib3.exceptions import HTTPError

TRF5_URL="http://www4.trf5.jus.br/cp/cp.do"

filePrecatorio = open("../dados/2018/precatorios/resultados/precatorios_2018_cancelados_para_refinar.txt", 'r')
Lines = filePrecatorio.readlines()

# Cria um array para popular os dados do arquivo
LISTA_PRECATORIO = []

# Popula o arquivo com os dados do arquivo
for line in Lines:
   LISTA_PRECATORIO.append(line.strip())

def formatarValor(str_valor):
    indexVirgula = str_valor.index(',')
    tamanhoPalavra = len(str_valor)
    novo_caracter = ''

    valorFormatado = str_valor[:indexVirgula] + novo_caracter + str_valor[indexVirgula + tamanhoPalavra:]
    return valorFormatado


def escrever_file_precatorio_cancelado_refinado(valorDepositado, cpf, nome, estado, local, precatorio):
    f = open(
        '../dados/2018/precatorios/resultados/precatorios_cancelados_todos_estados_qualquer_valor.txt', 'a')
    g = open(
        '../dados/2018/precatorios/resultados/precatorios_cancelados_todos_estados_qualquer_valor.csv', 'a')

    g.write(str(nome) + '|' + str(cpf) + '|' + str(estado) + '|' + str(local) + '|' + str(valorDepositado) + '|' + str(precatorio) + '\n')
    g.close()

    f.write(precatorio + '\n')
    f.close()

def escrever_file_falha_request(precatorio):
    f = open('../dados/2018/precatorios/resultados/arquivo_falha_request.txt', 'a')
    f.write(precatorio + '\n')
    f.close()

def ler_file_total_precatorio():
    LISTA_PRECATORIO_LIMPOS = []
    filePrecatorio = open("../dados/2018/precatorios/resultados/precatorios_2018_cancelados_para_refinar.txt", 'r')
    Lines = filePrecatorio.readlines()
    for line in Lines:
        LISTA_PRECATORIO_LIMPOS.append(line.strip())

    filePrecatorio.close()
    return LISTA_PRECATORIO_LIMPOS

def ler_file_precatorio_cancelado_refinado():
   LISTA_PRECATORIO_CANCELADO =[]
   filePrecatorio = open(
       "../dados/2018/precatorios/resultados/precatorios_cancelados_todos_estados_qualquer_valor.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_PRECATORIO_CANCELADO.append(line.strip())

   filePrecatorio.close()
   return LISTA_PRECATORIO_CANCELADO

def ler_arquivo_falha_request():
   LISTA_PRECATORIO_FALHA_REQUEST =[]
   filePrecatorio = open("../dados/2018/precatorios/resultados/arquivo_falha_request.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_PRECATORIO_FALHA_REQUEST.append(line.strip())

   filePrecatorio.close()
   return LISTA_PRECATORIO_FALHA_REQUEST

async def make_account():
    url = TRF5_URL
    f = open("../dados/2018/precatorios/resultados/arquivo_falha_request.txt", 'w')
    f.close()

    async with aiohttp.ClientSession() as session:
        post_tasks = []
        # now execute them all at once
        await asyncio.gather(*[do_post(session, url, precatorio) for precatorio in LISTA_PRECATORIO])

async def do_post(session, url, precatorio):

    try:

        if (precatorio in ler_file_precatorio_cancelado_refinado()):
            print(f"O RPV {precatorio} ja esta em um dos arquivos cancelados ou o outro")
        else:
            async with session.post(url, data ={
                "tipo": "xmlrpvprec",
                "filtroRPV_Precatorios": precatorio,
                "tipoproc": "P",
                "ordenacao": "p"
                    }) as response: data = await response.text()

            # Obtenção do Valor Depositado
            startValorDepositado = 'Dep&iuml;&iquest;&iquest;sito: R$ '
            endValorDepositado = ','
            valorDepositadoFiltrado = data.split(startValorDepositado)[1].split(endValorDepositado)[0]

            # Obtenção do PRC
            startPRC = '="14%">PRC'
            endPRC = '-'
            prcFiltrado = data.split(startPRC)[1].split(endPRC)[0]

            # Obtenção do Estado
            startEstado = '="14%">PRC' + precatorio + '-'
            endEstado = '</td>'
            estadoFiltrado = data.split(startEstado)[1].split(endEstado)[0]

            startLocal = 'JUIZ DE DIREITO '
            endLocal = '</td>'
            localFiltrado = data.split(startLocal)[1].split(endLocal)[0]

            startDoc = 'Documento: '
            endDoc = ','
            documentoFiltrado = data.split(startDoc)[1].split(endDoc)[0]

            startBeneficiario = 'Beneficiario: '
            endBeneficiario = ','
            beneficiarioFiltrado = data.split(startBeneficiario)[1].split(endBeneficiario)[0]

            if (prcFiltrado in ler_file_precatorio_cancelado_refinado()):
                print(f"PRECATORIO: {precatorio} já esta no arquivo de precatorio cancelado refinado")
            elif (prcFiltrado == precatorio):
                escrever_file_precatorio_cancelado_refinado(valorDepositadoFiltrado, documentoFiltrado, beneficiarioFiltrado, estadoFiltrado, localFiltrado , prcFiltrado)

    except HTTPError as aiohttp:

        if(precatorio in ler_file_precatorio_cancelado_refinado()):
            print(f"O PRECATORIO {precatorio} ja esta em um dos arquivos de precatorio refinado na exception {aiohttp}")
        else:
            escrever_file_falha_request(precatorio)

        print(f"Ocorreu um erro no HTTPError {aiohttp}")
    except Exception as err:
        if(precatorio in ler_arquivo_falha_request() or precatorio in ler_file_precatorio_cancelado_refinado()):
            print(f"O PRECATORIO {precatorio} já está gravado no arquivo de requições falhadas refinados")
        else:
            escrever_file_falha_request(precatorio)

        print(f"Ocorreu um erro no Exception Generico {err}")
    finally:
        print("Resumo do processamento!")

        lista_total_precatorios = ler_file_total_precatorio()
        lista_precatorios_cancelados = ler_file_precatorio_cancelado_refinado()
        lista_precatorios_falha_request = ler_arquivo_falha_request()

        print(f"Quantidade total precatorio cancelados: {len(lista_total_precatorios)} ")
        print(f"Quantidade precatorios cancelados refinados: {len(lista_precatorios_cancelados)}")
        print(f"Quantidade precatorios falha request: {len(lista_precatorios_falha_request)}")

        print("Conclusão do processamento!")

        if(len(lista_total_precatorios) == len(lista_precatorios_cancelados)):
            print("Todo os precatorios foram analisados com sucesso!")
        else:
            print(f"Ainda falta {(len(lista_total_precatorios) - (len(lista_precatorios_cancelados)  + len(lista_precatorios_falha_request)))} serem processados!")

def main():
   loop = asyncio.get_event_loop()
   loop.run_until_complete(make_account())
   loop.close()

main()