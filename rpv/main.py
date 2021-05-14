#importando tabelas em pdf usando o pytabula

# import tabula
# import requests
import aiohttp
import asyncio


from aiohttp import ClientSession
from pip._vendor.urllib3.exceptions import HTTPError

TRF5_URL="http://www4.trf5.jus.br/cp/cp.do"

#Procedimento 1 - Converter arquivo PDF em CSV
# tabula.convert_into("C:\\Users\\gdasi\\OneDrive\\Desktop\\necessidade-advogado-arthur\\precatorios\\2018_12106.pdf", "precatorios_2018.csv", output_format="csv", pages='2-215')

# Procedimento 2 - Abre no PDF e faz as limpezas necessárias


# Procedimento 3 - Obtem as linhas do arquivo e joga na variavel Lines


filePrecatorio = open("../dados/2019/precatorios_rpv_2019.txt", 'r')
Lines = filePrecatorio.readlines()

# Cria um array para popular os dados do arquivo
LISTA_RPV = []

# Popula o arquivo com os dados do arquivo
for line in Lines:
   LISTA_RPV.append(line.strip())

def escrever_file_precatorio_ativo(rpv):
    f = open('../dados/2019/rpv/resultados/precatorios_ativos.txt', 'a')
    f.write(rpv+'\n')
    f.close()

def escrever_file_precatorio_cancelado(rpv):
    f = open('../dados/2019/rpv/resultados/precatorios_cancelados.txt', 'a')
    f.write(rpv + '\n')
    f.close()

def escrever_file_falha_request(rpv):
    f = open('../dados/2019/arquivo_falha_request.txt', 'a')
    f.write(rpv + '\n')
    f.close()

def ler_file_total_precatorio():
    LISTA_RPV_LIMPOS = []
    filePrecatorio = open("../dados/2019/precatorios_rpv_2019.txt", 'r')
    Lines = filePrecatorio.readlines()
    for line in Lines:
        LISTA_RPV_LIMPOS.append(line.strip())

    filePrecatorio.close()
    return LISTA_RPV_LIMPOS

def ler_file_precatorio_ativo():
   LISTA_RPV_ATIVO =[]
   filePrecatorio = open("../dados/2019/rpv/resultados/precatorios_ativos.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_RPV_ATIVO.append(line.strip())

   filePrecatorio.close()
   return LISTA_RPV_ATIVO

def ler_file_precatorio_cancelado():
   LISTA_RPV_CANCELADO =[]
   filePrecatorio = open("../dados/2019/rpv/resultados/precatorios_cancelados.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_RPV_CANCELADO.append(line.strip())

   filePrecatorio.close()
   return LISTA_RPV_CANCELADO

def ler_arquivo_falha_request():
   LISTA_RPV_FALHA_REQUEST =[]
   filePrecatorio = open("../dados/2019/arquivo_falha_request.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_RPV_FALHA_REQUEST.append(line.strip())

   filePrecatorio.close()
   return LISTA_RPV_FALHA_REQUEST

async def make_account():
    url = TRF5_URL
    f = open('../dados/2019/arquivo_falha_request.txt', 'w')
    f.close()

    async with aiohttp.ClientSession() as session:
        post_tasks = []
        # now execute them all at once
        await asyncio.gather(*[do_post(session, url, rpv) for rpv in LISTA_RPV])

async def do_post(session, url, rpv):

    try:

        if (rpv in ler_file_precatorio_ativo() or rpv in ler_file_precatorio_cancelado()):
            print(f"O RPV {rpv} ja esta em um dos arquivos de precatorio")
        else:
            async with session.post(url, data ={
                "tipo": "xmlrpvprec",
                "filtroRPV_Precatorios": rpv,
                "tipoproc": "R",
                "ordenacao": "p"
                    }) as response: data = await response.text()
            if("Cancelamento de Precat&oacute;rio/RPV" in data):

              if(rpv in ler_file_precatorio_cancelado()):
                  print(f"RPV: {rpv} já esta no arquivo")
              else:
                  escrever_file_precatorio_cancelado(rpv)

            else:
              if(rpv in ler_file_precatorio_ativo()):
                  print(f"RPV: {rpv} já está no arquivo ativo")
              else:
                  escrever_file_precatorio_ativo(rpv)

    except HTTPError as aiohttp:

        if(rpv in ler_file_precatorio_ativo() or rpv in ler_file_precatorio_cancelado()):
            print(f"O RPV {rpv} ja esta em um dos arquivos de precatorio")
        else:
            escrever_file_falha_request(rpv)
    except Exception as err:
        if(rpv in ler_arquivo_falha_request() or (rpv in ler_file_precatorio_ativo() and rpv in ler_file_precatorio_cancelado())):
            print(f"O RPV {rpv} já está gravado no arquivo de requições falhadas")
        else:
            escrever_file_falha_request(rpv)
    finally:
        print("Resumo do processamento!")

        lista_total_precatorios = ler_file_total_precatorio()
        lista_precatorios_ativos = ler_file_precatorio_ativo()
        lista_precatorios_cancelados = ler_file_precatorio_cancelado()
        lista_precatorios_falha_request = ler_arquivo_falha_request()

        print(f"Quantidade total precatorio: {len(lista_total_precatorios)} ")
        print(f"Quantidade precatorios ativos: {len(lista_precatorios_ativos)}")
        print(f"Quantidade precatorios cancelados: {len(lista_precatorios_cancelados)}")
        print(f"Quantidade precatorios falha request: {len(lista_precatorios_falha_request)}")

        print("Conclusão do processamento!")

        if(len(lista_total_precatorios) == (len(lista_precatorios_cancelados) + len(lista_precatorios_ativos))):
            print("Todo os precatorios foram analisados com sucesso!")
        else:
            print(f"Ainda falta {(len(lista_total_precatorios) - (len(lista_precatorios_cancelados) + len(lista_precatorios_ativos)))} serem processados!")

def main():
   loop = asyncio.get_event_loop()
   loop.run_until_complete(make_account())
   loop.close()

main()