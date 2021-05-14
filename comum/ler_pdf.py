import tabula
import sys
import os.path


def converterPDFToCsv():
  tabula.convert_into("C:\\Users\\gdasi\\OneDrive\\Desktop\\necessidade-advogado-arthur\\precatorios\\2019\\precatorios_2019_por_processo.pdf",
                      "precatorios_limpo_2019.csv", output_format="csv", pages='1-168')

def main():
    converterPDFToCsv()

main()