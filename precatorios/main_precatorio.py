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


filePrecatorio = open("../dados/2018/precatorios/precatorios_2018.txt", 'r')
Lines = filePrecatorio.readlines()

# Cria um array para popular os dados do arquivo
LISTA_PRECATORIO = []

# Popula o arquivo com os dados do arquivo
for line in Lines:
   LISTA_PRECATORIO.append(line.strip())

def escrever_file_precatorio_ativo(precatorio):
    f = open('../dados/2018/precatorios/resultados/precatorios_2018_ativos.txt', 'a')
    f.write(precatorio+'\n')
    f.close()

def escrever_file_precatorio_cancelado(precatorio):
    f = open('../dados/2018/precatorios/resultados/precatorios_2018_cancelados.txt', 'a')
    f.write(precatorio + '\n')
    f.close()

def escrever_file_falha_request(precatorio):
    f = open('../dados/2018/precatorios/precatorio_falha_request.txt', 'a')
    f.write(precatorio + '\n')
    f.close()

def ler_file_total_precatorio():
    LISTA_PRECATORIO_LIMPOS = []
    filePrecatorio = open("../dados/2018/precatorios/precatorios_2018.txt", 'r')
    Lines = filePrecatorio.readlines()
    for line in Lines:
        LISTA_PRECATORIO_LIMPOS.append(line.strip())

    filePrecatorio.close()
    return LISTA_PRECATORIO_LIMPOS

def ler_file_precatorio_ativo():
   LISTA_PRECATORIO_ATIVO = []
   filePrecatorio = open("../dados/2018/precatorios/resultados/precatorios_2018_ativos.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_PRECATORIO_ATIVO.append(line.strip())

   filePrecatorio.close()
   return LISTA_PRECATORIO_ATIVO

def ler_file_precatorio_cancelado():
   LISTA_PRECATORIO_CANCELADO =[]
   filePrecatorio = open("../dados/2018/precatorios/resultados/precatorios_2018_cancelados.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_PRECATORIO_CANCELADO.append(line.strip())

   filePrecatorio.close()
   return LISTA_PRECATORIO_CANCELADO

def ler_arquivo_falha_request():
   LISTA_PRECATORIO_FALHA_REQUEST =[]
   filePrecatorio = open("../dados/2018/precatorios/precatorio_falha_request.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_PRECATORIO_FALHA_REQUEST.append(line.strip())

   filePrecatorio.close()
   return LISTA_PRECATORIO_FALHA_REQUEST

async def make_account():
    url = TRF5_URL
    f = open('../dados/2018/precatorios/precatorio_falha_request.txt', 'w')
    f.close()

    async with aiohttp.ClientSession() as session:
        post_tasks = []
        # now execute them all at once
        await asyncio.gather(*[do_post(session, url, precatorio) for precatorio in LISTA_PRECATORIO])

async def do_post(session, url, precatorio):

    try:

        if (precatorio in ler_file_precatorio_ativo() or precatorio in ler_file_precatorio_cancelado()):
            print(f"O PRECATORIO {precatorio} ja esta em um dos arquivos de precatorio")
        else:
            async with session.post(url, data ={
                "tipo": "xmlrpvprec",
                "filtroRPV_Precatorios": precatorio,
                "tipoproc": "P",
                "ordenacao": "p"
                    }) as response: data = await response.text()
            if("Cancelamento de Precat&oacute;rio/RPV" in data):

              if(precatorio in ler_file_precatorio_cancelado()):
                  print(f"PRECATORIO: {precatorio} já esta no arquivo")
              else:
                  escrever_file_precatorio_cancelado(precatorio)

            else:
              if(precatorio in ler_file_precatorio_ativo()):
                  print(f"PRECATORIO: {precatorio} já está no arquivo ativo")
              else:
                  escrever_file_precatorio_ativo(precatorio)

    except HTTPError as aiohttp:

        if(precatorio in ler_file_precatorio_ativo() or precatorio in ler_file_precatorio_cancelado()):
            print(f"O PRECATORIO {precatorio} ja esta em um dos arquivos de precatorio")
        else:
            escrever_file_falha_request(precatorio)
    except Exception as err:
        if(precatorio in ler_arquivo_falha_request() or (precatorio in ler_file_precatorio_ativo() and precatorio in ler_file_precatorio_cancelado())):
            print(f"O PRECATORIO {precatorio} já está gravado no arquivo de requisições falhadas")
        else:
            escrever_file_falha_request(precatorio)
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