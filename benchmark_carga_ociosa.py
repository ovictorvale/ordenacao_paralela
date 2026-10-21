
import os
import random
import time
import multiprocessing as mp

from concurrent.futures import ProcessPoolExecutor

from mergesort_paralelo import merge_sort_seq, merge
from tabelas import imprimir_tabela


# Barreira utilizada pelos processos
barreira_worker = None


def configurar_worker(barreira):
    global barreira_worker
    barreira_worker = barreira


# Ordena um bloco e mede o tempo de espera
def ordenar_bloco(bloco):
    inicio = time.perf_counter()

    bloco_ordenado = merge_sort_seq(bloco)

    tempo_trabalho = time.perf_counter() - inicio

    # Aguarda os demais processos terminarem
    inicio_espera = time.perf_counter()
    barreira_worker.wait(timeout=180)
    tempo_espera = time.perf_counter() - inicio_espera

    return (
        os.getpid(),
        bloco_ordenado,
        tempo_trabalho,
        tempo_espera
    )


def executar_benchmark():
    n = 1_000_000
    num_workers = 4

    gerador = random.Random(42)
    dados = [
        gerador.randint(1, 10_000_000)
        for _ in range(n)
    ]

    # Divide o vetor em quatro blocos
    tamanho_bloco = (n + num_workers - 1) // num_workers

    blocos = [
        dados[i:i + tamanho_bloco]
        for i in range(0, n, tamanho_bloco)
    ]

    contexto = mp.get_context("spawn")
    barreira = contexto.Barrier(num_workers)

    print("\n=== CARGA OCIOSA - MERGESORT ===")
    print(f"Elementos: {n:,}")
    print(f"Processos: {num_workers}")

    inicio_total = time.perf_counter()

    with ProcessPoolExecutor(
        max_workers=num_workers,
        mp_context=contexto,
        initializer=configurar_worker,
        initargs=(barreira,)
    ) as executor:

        futures = [
            executor.submit(ordenar_bloco, bloco)
            for bloco in blocos
        ]

        resultados = []
        espera_principal = 0

        for future in futures:
            inicio = time.perf_counter()
            resultados.append(future.result())
            espera_principal += (
                time.perf_counter() - inicio
            )

    # Intercalacao sequencial dos blocos
    blocos_ordenados = [item[1] for item in resultados]

    while len(blocos_ordenados) > 1:
        novos_blocos = []

        for i in range(0, len(blocos_ordenados), 2):
            if i + 1 < len(blocos_ordenados):
                novos_blocos.append(
                    merge(
                        blocos_ordenados[i],
                        blocos_ordenados[i + 1]
                    )
                )
            else:
                novos_blocos.append(blocos_ordenados[i])

        blocos_ordenados = novos_blocos

    tempo_total = time.perf_counter() - inicio_total
    resultado_final = blocos_ordenados[0]

    # Validacao
    assert resultado_final == sorted(dados), (
        "Erro na ordenacao!"
    )

    linhas = []
    soma_espera = 0

    for indice, item in enumerate(resultados):
        pid, _, trabalho, espera = item

        soma_espera += espera

        percentual = (
            espera / (trabalho + espera)
        ) * 100

        linhas.append([
            f"Worker {indice + 1}",
            str(pid),
            f"{trabalho:.4f}",
            f"{espera:.4f}",
            f"{percentual:.2f}%"
        ])

    imprimir_tabela(
        "TEMPO DE TRABALHO E ESPERA",
        [
            "Processo",
            "PID",
            "Trabalho (s)",
            "Espera (s)",
            "Espera (%)"
        ],
        linhas
    )

    # Espera acumulada relativa ao tempo total
    percentual_global = (
        soma_espera / (num_workers * tempo_total)
    ) * 100

    print(f"\nTempo total: {tempo_total:.4f} s")
    print(f"Espera acumulada dos workers: {soma_espera:.4f} s")
    print(f"Espera do processo principal (.result): {espera_principal:.4f} s")
    print(f"Espera sincronizada relativa ao total: {percentual_global:.2f}%")

    print("\nOrdenacao validada com sucesso!")


if __name__ == "__main__":
    executar_benchmark()
