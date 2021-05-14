def formatarValor(str_valor):
    indexVirgula = str_valor.index(',')
    tamanhoPalavra = len(str_valor)
    novo_caracter = ''

    valorFormatado = str_valor[:indexVirgula] + novo_caracter + str_valor[indexVirgula + tamanhoPalavra:]
    print(valorFormatado)

formatarValor('10.389,88')