import tabula

# Procedimento 1 - Converter arquivo PDF em CSV
# Procedimento 2 - Abre no PDF e faz as limpezas necessárias
# Procedimento 3 - Obtem as linhas do arquivo e joga na variavel Lines

def converterPDFToCsv():
  tabula.convert_into("C:\\Users\\User\\PyCharmProjects\\projeto-obtencao-precatorio\\pdf\\2018\\2018.pdf",
                      "C:\\Users\\User\\PyCharmProjects\\projeto-obtencao-precatorio\\pdf\\2018\\2018_versao01.csv", output_format="csv", pages='2-215')

def main():
    converterPDFToCsv()

main()