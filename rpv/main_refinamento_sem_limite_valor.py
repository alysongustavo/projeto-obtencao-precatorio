#importando tabelas em pdf usando o pytabula

# import tabula
# import requests
import aiohttp
import asyncio
import locale



from aiohttp import ClientSession
from pip._vendor.urllib3.exceptions import HTTPError

TRF5_URL="http://www4.trf5.jus.br/cp/cp.do"

#Procedimento 1 - Converter arquivo PDF em CSV
# tabula.convert_into("C:\\Users\\gdasi\\OneDrive\\Desktop\\necessidade-advogado-arthur\\precatorios\\2018_12106.pdf", "precatorios_2018.csv", output_format="csv", pages='2-215')

# Procedimento 2 - Abre no PDF e faz as limpezas necessárias


# Procedimento 3 - Obtem as linhas do arquivo e joga na variavel Lines


filePrecatorio = open("../dados/2018/rpv/resultados/precatorios_cancelados_para_refinar.txt", 'r')
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


def escrever_file_precatorio_cancelado_refinado(valorDepositado, valorDevolvido, cpf, nome, estado, rpv):
    f = open(
        '../dados/2018/rpv/resultados/pb_quaisquer_valores/precatorios_cancelados_pb_qualquer_valor_somente_rpv.txt', 'a')
    g = open('../dados/2018/rpv/resultados/pb_quaisquer_valores/precatorios_cancelados_pb_qualquer_valor.csv', 'a')

    g.write(str(nome) + '|' + str(cpf) + '|' + str(estado) + '|' + str(valorDepositado) + '|' + str(valorDevolvido) + '|' + str(rpv) + '\n')
    g.close()

    f.write(rpv + '\n')
    f.close()

def escrever_file_precatorio_cancelado_refinado_nao_pb(rpv):
        f = open('../dados/2018/rpv/resultados/pb_quaisquer_valores/precatorios_cancelados_nao_pb.txt', 'a')
        f.write(rpv + '\n')
        f.close()

def escrever_file_falha_request(rpv):
    f = open('../dados/2018/rpv/resultados/pb_quaisquer_valores/arquivo_falha_request.txt', 'a')
    f.write(rpv + '\n')
    f.close()

def ler_file_total_precatorio():
    LISTA_RPV_LIMPOS = []
    filePrecatorio = open("../dados/2018/rpv/resultados/precatorios_cancelados_para_refinar.txt", 'r')
    Lines = filePrecatorio.readlines()
    for line in Lines:
        LISTA_RPV_LIMPOS.append(line.strip())

    filePrecatorio.close()
    return LISTA_RPV_LIMPOS

def ler_file_precatorio_cancelado_refinado():
   LISTA_RPV_CANCELADO =[]
   filePrecatorio = open(
       "../dados/2018/rpv/resultados/pb_quaisquer_valores/precatorios_cancelados_pb_qualquer_valor_somente_rpv.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_RPV_CANCELADO.append(line.strip())

   filePrecatorio.close()
   return LISTA_RPV_CANCELADO

def ler_file_precatorio_cancelado_refinado_nao_pb():
   LISTA_RPV_CANCELADO =[]
   filePrecatorio = open("../dados/2018/rpv/resultados/pb_quaisquer_valores/precatorios_cancelados_nao_pb.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_RPV_CANCELADO.append(line.strip())

   filePrecatorio.close()
   return LISTA_RPV_CANCELADO

def ler_arquivo_falha_request():
   LISTA_RPV_FALHA_REQUEST =[]
   filePrecatorio = open("../dados/2018/rpv/resultados/pb_quaisquer_valores/arquivo_falha_request.txt", 'r')
   Lines = filePrecatorio.readlines()
   for line in Lines:
       LISTA_RPV_FALHA_REQUEST.append(line.strip())

   filePrecatorio.close()
   return LISTA_RPV_FALHA_REQUEST

async def make_account():
    url = TRF5_URL
    f = open('../dados/2018/rpv/resultados/pb_quaisquer_valores/arquivo_falha_request.txt', 'w')
    f.close()

    async with aiohttp.ClientSession() as session:
        post_tasks = []
        # now execute them all at once
        await asyncio.gather(*[do_post(session, url, rpv) for rpv in LISTA_RPV])

async def do_post(session, url, rpv):

    try:

        if (rpv in ler_file_precatorio_cancelado_refinado() or rpv in ler_file_precatorio_cancelado_refinado_nao_pb()):
            print(f"O RPV {rpv} ja esta em um dos arquivos cancelados pb ou o outro")
        else:
            async with session.post(url, data ={
                "tipo": "xmlrpvprec",
                "filtroRPV_Precatorios": rpv,
                "tipoproc": "R",
                "ordenacao": "p"
                    }) as response: data = await response.text()

            # Obtenção do Valor Depositado
            startValorDepositado = 'Dep&iuml;&iquest;&iquest;sito: R$ '
            endValorDepositado = ','
            valorDepositado = data.split(startValorDepositado)[1].split(endValorDepositado)[0]
            #valorDepositadoConvertido = formatarValor(rpvValorDepositado)
            #valorRemovendoPonto = valorDepositadoConvertido.replace('.', '')

            # Obtenção do Valor Devolvido
            startValorDevolvido = 'Valor Devolvido: R$ '
            endValorDevolvido = ','
            valorDevolvido = data.split(startValorDevolvido)[1].split(endValorDevolvido)[0]
            #valorDevolvidoConvertido = formatarValor(rpvValorDevolvido)
            #valorRemovendoPonto = valorDevolvidoConvertido.replace('.', '')

            # Obtenção do RPV
            start = '="14%">RPV'
            end = '-PB'
            rpvPB = data.split(start)[1].split(end)[0]

            startDoc = 'Documento: '
            endDoc = ','
            documento = data.split(startDoc)[1].split(endDoc)[0]

            startBeneficiario = 'Beneficiario: '
            endBeneficiario = ','
            beneficiario = data.split(startBeneficiario)[1].split(endBeneficiario)[0]

            if (rpv in ler_file_precatorio_cancelado_refinado()):
                print(f"RPV: {rpv} já esta no arquivo de precatorio cancelado refinado")
            elif (rpvPB == rpv):
                escrever_file_precatorio_cancelado_refinado(valorDepositado, valorDevolvido, documento, beneficiario, 'PB', rpv)
            else:
                escrever_file_precatorio_cancelado_refinado_nao_pb(rpv)
                print(f"RPV: {rpv} não se adequa a necessidade de Artur")

    except HTTPError as aiohttp:

        if(rpv in ler_file_precatorio_cancelado_refinado() or rpv in ler_file_precatorio_cancelado_refinado_nao_pb()):
            print(f"O RPV {rpv} ja esta em um dos arquivos de precatorio refinado na exception {aiohttp}")
        else:
            escrever_file_falha_request(rpv)

        print(f"Ocorreu um erro no HTTPError {aiohttp}")
    except Exception as err:
        if(rpv in ler_arquivo_falha_request() or rpv in ler_file_precatorio_cancelado_refinado()):
            print(f"O RPV {rpv} já está gravado no arquivo de requições falhadas refinados")
        else:
            escrever_file_falha_request(rpv)

        print(f"Ocorreu um erro no Exception Generico {err}")
    finally:
        print("Resumo do processamento!")

        lista_total_precatorios = ler_file_total_precatorio()
        lista_precatorios_cancelados = ler_file_precatorio_cancelado_refinado()
        lista_precatorios_cancelados_arthur_nao_precisa = ler_file_precatorio_cancelado_refinado_nao_pb()
        lista_precatorios_falha_request = ler_arquivo_falha_request()

        print(f"Quantidade total precatorio cancelados: {len(lista_total_precatorios)} ")
        print(f"Quantidade precatorios cancelados refinados: {len(lista_precatorios_cancelados)}")
        print(f"Quantidade precatorios cancelados refinados artur não precisa: {len(lista_precatorios_cancelados_arthur_nao_precisa)}")
        print(f"Quantidade precatorios falha request: {len(lista_precatorios_falha_request)}")

        print("Conclusão do processamento!")

        if(len(lista_total_precatorios) == (len(lista_precatorios_cancelados) + len(lista_precatorios_cancelados_arthur_nao_precisa))):
            print("Todo os precatorios foram analisados com sucesso!")
        else:
            print(f"Ainda falta {(len(lista_total_precatorios) - (len(lista_precatorios_cancelados) + len(lista_precatorios_cancelados_arthur_nao_precisa) + len(lista_precatorios_falha_request)))} serem processados!")

def main():
   loop = asyncio.get_event_loop()
   loop.run_until_complete(make_account())
   loop.close()

main()