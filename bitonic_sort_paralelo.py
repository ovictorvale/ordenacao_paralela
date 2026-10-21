
import random
import time
import multiprocessing as mp

from tabelas import calcular_metricas, imprimir_tabela


# Verifica se N e potencia de 2
def validar_tamanho(n):
    if n < 1 or (n & (n - 1)) != 0:
        raise ValueError("N deve ser uma potencia de 2!")


# Bitonic Sort Sequencial
def bitonic_sort_seq(vetor):
    n = len(vetor)
    validar_tamanho(n)

    dados = vetor.copy()
    k = 2

    while k <= n:
        j = k // 2

        while j > 0:
            for i in range(n):
                parceiro = i ^ j

                if parceiro > i:
                    crescente = (i & k) == 0

                    if (
                        (crescente and dados[i] > dados[parceiro])
                        or
                        (not crescente and dados[i] < dados[parceiro])
                    ):
                        dados[i], dados[parceiro] = (
                            dados[parceiro], dados[i]
                        )

            j //= 2

        k *= 2

    return dados


# Trabalho de cada processo
def worker_bitonic(
    dados, n, identificador, num_workers, barreira
):
    inicio = identificador * n // num_workers
    fim = (identificador + 1) * n // num_workers

    k = 2

    while k <= n:
        j = k // 2

        while j > 0:
            for i in range(inicio, fim):
                parceiro = i ^ j

                if parceiro > i:
                    crescente = (i & k) == 0

                    if (
                        (crescente and dados[i] > dados[parceiro])
                        or
                        (not crescente and dados[i] < dados[parceiro])
                    ):
                        dados[i], dados[parceiro] = (
                            dados[parceiro], dados[i]
                        )

            # Sincroniza os processos antes da proxima etapa
            barreira.wait()
            j //= 2

        k *= 2


# Bitonic Sort Paralelo
def bitonic_sort_paralelo(vetor, num_workers=4):
    n = len(vetor)
    validar_tamanho(n)

    if num_workers < 1:
        raise ValueError("Numero de processos invalido!")

    if num_workers == 1 or n == 1:
        return bitonic_sort_seq(vetor)

    contexto = mp.get_context("spawn")

    dados = contexto.Array("i", vetor, lock=False)
    barreira = contexto.Barrier(num_workers)

    processos = []

    for identificador in range(num_workers):
        processo = contexto.Process(
            target=worker_bitonic,
            args=(
                dados, n, identificador,
                num_workers, barreira
            )
        )

        processos.append(processo)
        processo.start()

    for processo in processos:
        processo.join()

    if any(p.exitcode != 0 for p in processos):
        raise RuntimeError("Falha na execucao paralela!")

    return list(dados)


# Benchmark
def executar_benchmark():
    n = 8_192
    num_workers = 4

    gerador = random.Random(42)
    dados = [
        gerador.randint(1, 100_000)
        for _ in range(n)
    ]

    print("\n=== BITONIC SORT SEQUENCIAL VS PARALELO ===")
    print(f"Elementos: {n:,}")
    print(f"Processos: {num_workers}")

    # Execucao sequencial
    inicio = time.perf_counter()
    resultado_seq = bitonic_sort_seq(dados.copy())
    tempo_serial = time.perf_counter() - inicio

    # Execucao paralela
    inicio = time.perf_counter()
    resultado_par = bitonic_sort_paralelo(
        dados.copy(),
        num_workers
    )
    tempo_paralelo = time.perf_counter() - inicio

    # Validacao
    assert resultado_seq == resultado_par == sorted(dados), (
        "Erro na ordenacao!"
    )

    # Metricas
    speedup, eficiencia = calcular_metricas(
        tempo_serial,
        tempo_paralelo,
        num_workers
    )

    reducao = (
        (tempo_serial - tempo_paralelo) / tempo_serial
    ) * 100

    situacao = (
        "Paralelo mais rapido"
        if tempo_paralelo < tempo_serial
        else "Paralelo mais lento"
        if tempo_paralelo > tempo_serial
        else "Tempos iguais"
    )

    resultados = [[
        f"{n:,}",
        f"{tempo_serial:.4f}",
        f"{tempo_paralelo:.4f}",
        f"{speedup:.2f}x",
        f"{eficiencia:.2f}%",
        f"{reducao:+.2f}%",
        situacao
    ]]

    imprimir_tabela(
        "RESULTADOS - BITONIC SORT",
        [
            "N",
            "Serial (s)",
            "Paralelo (s)",
            "Speedup",
            "Eficiencia",
            "Reducao (%)",
            "Situacao"
        ],
        resultados
    )

    print("\nTodos os resultados foram validados!")


if __name__ == "__main__":
    executar_benchmark()
