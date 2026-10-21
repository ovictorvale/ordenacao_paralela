
def calcular_metricas(tempo_serial, tempo_paralelo, processos):
    if tempo_paralelo <= 0 or processos <= 0:
        raise ValueError("Tempo e quantidade de processos devem ser positivos.")

    speedup = tempo_serial / tempo_paralelo
    eficiencia = (speedup / processos) * 100

    return speedup, eficiencia


def imprimir_tabela(titulo, cabecalhos, linhas):
    larguras = [len(str(c)) for c in cabecalhos]

    for linha in linhas:
        if len(linha) != len(cabecalhos):
            raise ValueError("Quantidade de colunas incorreta.")

        for i, valor in enumerate(linha):
            larguras[i] = max(larguras[i], len(str(valor)))

    def formatar(linha):
        celulas = [
            str(valor).ljust(larguras[i])
            for i, valor in enumerate(linha)
        ]
        return "| " + " | ".join(celulas) + " |"

    separador = "+-" + "-+-".join(
        "-" * largura for largura in larguras
    ) + "-+"

    print(f"\n{titulo}")
    print(separador)
    print(formatar(cabecalhos))
    print(separador)

    for linha in linhas:
        print(formatar(linha))

    print(separador)
