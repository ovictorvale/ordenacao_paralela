
import random
import time
import multiprocessing as mp

from mergesort_paralelo import (
    merge_sort_seq,
    parallel_merge_sort
)
from tabelas import calcular_metricas, imprimir_tabela


# Odd-Even Sequencial
def odd_even_sort_seq(vetor):
    dados = vetor.copy()
    n = len(dados)
    ordenado = False

    while not ordenado:
        ordenado = True

        # Alterna fase impar e fase par
        for fase in (1, 0):
            for i in range(fase, n - 1, 2):
                if dados[i] > dados[i + 1]:
                    dados[i], dados[i + 1] = dados[i + 1], dados[i]
                    ordenado = False

    return dados


# Trabalho realizado por cada processo
def worker_odd_even(
    dados, n, identificador, num_workers,
    barreira, trocas
):
    while True:
        # Cada processo reinicia seu indicador
        trocas[identificador] = 0
        barreira.wait()

        for fase in (1, 0):
            total_pares = len(range(fase, n - 1, 2))

            inicio = identificador * total_pares // num_workers
            fim = (identificador + 1) * total_pares // num_workers

            # Cada processo recebe pares independentes
            for k in range(inicio, fim):
                i = fase + 2 * k

                if dados[i] > dados[i + 1]:
                    dados[i], dados[i + 1] = dados[i + 1], dados[i]
                    trocas[identificador] = 1

            # Aguarda todos terminarem a fase
            barreira.wait()

        # Verifica se ainda ocorreram trocas
        continuar = any(trocas)
        barreira.wait()

        if not continuar:
            break


# Odd-Even Paralelo
def odd_even_sort_paralelo(vetor, num_workers=4):
    if num_workers < 1:
        raise ValueError("Numero de processos invalido!")

    if len(vetor) < 2 or num_workers == 1:
        return odd_even_sort_seq(vetor)

    contexto = mp.get_context("spawn")

    # Vetor compartilhado entre os processos
    dados = contexto.Array("i", vetor, lock=False)

    # Sincronizacao das fases
    barreira = contexto.Barrier(num_workers)

    # Registra se cada processo realizou trocas
    trocas = contexto.Array(
        "i", [0] * num_workers, lock=False
    )

    processos = []

    for identificador in range(num_workers):
        processo = contexto.Process(
            target=worker_odd_even,
            args=(
                dados,
                len(vetor),
                identificador,
                num_workers,
                barreira,
                trocas
            )
        )
        processos.append(processo)
        processo.start()

    # Aguarda os processos terminarem
    for processo in processos:
        processo.join()

    if any(p.exitcode != 0 for p in processos):
        raise RuntimeError("Falha na execucao paralela!")

    return list(dados)


# Benchmark dos dois algoritmos
def executar_benchmark():
    n = 50_000
    num_workers = 4

    # Quatro blocos para o MergeSort
    threshold = max(1, n // num_workers)

    gerador = random.Random(42)

    dados = [
        gerador.randint(1, 100_000)
        for _ in range(n)
    ]

    resultado_esperado = sorted(dados)

    resultados = []

    print("\n=== ODD-EVEN VS MERGESORT ===")
    print(f"Elementos: {n:,}")
    print(f"Processos: {num_workers}")

    algoritmos = [
        ("Odd-Even", odd_even_sort_seq, odd_even_sort_paralelo),
        ("MergeSort", merge_sort_seq, parallel_merge_sort)
    ]

    for nome, funcao_seq, funcao_par in algoritmos:
        print(f"\nTestando {nome}...")

        # Execucao sequencial
        inicio = time.perf_counter()
        resultado_seq = funcao_seq(dados.copy())
        tempo_serial = time.perf_counter() - inicio

        # Execucao paralela
        inicio = time.perf_counter()

        if nome == "MergeSort":
            resultado_par = funcao_par(
                dados.copy(),
                num_workers=num_workers,
                threshold=threshold
            )
        else:
            resultado_par = funcao_par(
                dados.copy(),
                num_workers=num_workers
            )

        tempo_paralelo = time.perf_counter() - inicio

        # Valida os resultados
        assert resultado_seq == resultado_esperado
        assert resultado_par == resultado_esperado

        # Calcula as metricas
        speedup, eficiencia = calcular_metricas(
            tempo_serial,
            tempo_paralelo,
            num_workers
        )

        reducao = (
            (tempo_serial - tempo_paralelo) / tempo_serial
        ) * 100

        resultados.append([
            nome,
            f"{tempo_serial:.4f}",
            f"{tempo_paralelo:.4f}",
            f"{speedup:.2f}x",
            f"{eficiencia:.2f}%",
            f"{reducao:+.2f}%"
        ])

    imprimir_tabela(
        "COMPARACAO DE DESEMPENHO",
        [
            "Algoritmo",
            "Serial (s)",
            "Paralelo (s)",
            "Speedup",
            "Eficiencia",
            "Reducao (%)"
        ],
        resultados
    )

    print("\nTodos os resultados foram validados!")


if __name__ == "__main__":
    executar_benchmark()
