#importando tabelas em pdf usando o pytabula

# import tabula
# import requests
import aiohttp
import asyncio
import re


from aiohttp import ClientSession
from pip._vendor.urllib3.exceptions import HTTPError

TRF5_URL="http://www4.trf5.jus.br/cp/cp.do"

# Procedimento 2 - Abre no PDF e faz as limpezas necessárias


# Procedimento 3 - Obtem as linhas do arquivo e joga na variavel Lines

def obterProcessos():
    LISTA_PROCESSOS = [];
    filePrecatorio = open("../dados/2019/precatorios_processos_limpo_2019.txt")
    Lines = filePrecatorio.readlines()
    for line in Lines:
        LISTA_PROCESSOS.append(line.strip())
    filePrecatorio.close()
    return LISTA_PROCESSOS

def escrever_file_precatorio_rpv_2019(rpv):
    f = open('../dados/2019/precatorios_rpv_2019.txt', 'a')
    f.write(rpv+'\n')
    f.close()

def escrever_file_falha_request(rpv):
    f = open('../dados/2019/arquivo_falha_request_rpv_2019.txt', 'a')
    f.write(rpv + '\n')
    f.close()

def ler_file_precatorio_rpv_2019():
    LISTA_RPV_LIMPOS = []
    filePrecatorio = open("../dados/2019/precatorios_rpv_2019.txt", 'r')
    Lines = filePrecatorio.readlines()
    for line in Lines:
        LISTA_RPV_LIMPOS.append(line.strip())

    filePrecatorio.close()
    return LISTA_RPV_LIMPOS

def ler_arquivo_falha_request_rpv_2019():
   LISTA_RPV_FALHA_REQUEST =[]
   filePrecatorio = open("../dados/2019/arquivo_falha_request_rpv_2019.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_RPV_FALHA_REQUEST.append(line.strip())

   filePrecatorio.close()
   return LISTA_RPV_FALHA_REQUEST

async def make_account():
    url = TRF5_URL
    f = open('../dados/2019/arquivo_falha_request_rpv_2019.txt', 'w')
    f.close()

    async with aiohttp.ClientSession() as session:
        post_tasks = []
        # now execute them all at once
        await asyncio.gather(*[do_post(session, url, processo) for processo in obterProcessos()])

async def do_post(session, url, processo):

    try:

        if (processo in ler_file_precatorio_rpv_2019()):
            print(f"O Processo {processo} ja esta em um dos arquivos de precatorio com processo")
        else:
            async with session.post(url, data ={
                "tipo": "xmlproc",
                "filtro": processo,
                "tipoproc": "T"
                    }) as response: data = await response.text()

            start = '(PRC'
            end = '-'

            rpv = data.split(start)[1].split(end)[0]

            if(rpv in ler_file_precatorio_rpv_2019()):
                print(f"O rpv {rpv} ja esta no arquivo de rpv")
            else:
                escrever_file_precatorio_rpv_2019(rpv)
    except HTTPError as aiohttp:
                print(aiohttp)
    except Exception as err:
                print(err)
    finally:
        print("Resumo do processamento!")

        lista_total_precatorios_processos = obterProcessos()
        tamanho_total_precatorios_processos = len(lista_total_precatorios_processos)
        lista_precatorios_rpv = ler_file_precatorio_rpv_2019()
        tamanho_total_precatorio_rpv = len(lista_precatorios_rpv)
        lista_rpv_falhado = ler_arquivo_falha_request_rpv_2019()
        tamanho_lista_rpv_falhado = len(lista_rpv_falhado)

        print("Conclusão do processamento!")

        print(f"Quantidade total precatorio processos: {tamanho_total_precatorios_processos} ")
        print(f"Quantidade total precatorio rpv: {tamanho_total_precatorio_rpv}")

        if(tamanho_total_precatorios_processos == (tamanho_total_precatorio_rpv - 58)):
            print("Todo os precatorios foram analisados com sucesso!")
        else:
            print(f"Ainda falta {tamanho_total_precatorios_processos - (tamanho_total_precatorio_rpv - 58)} serem processados!")

def main():
   loop = asyncio.get_event_loop()
   loop.run_until_complete(make_account())
   loop.close()

main()