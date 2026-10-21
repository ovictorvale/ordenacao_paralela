
import random
import time
import math

from mergesort_paralelo import merge_sort_seq, parallel_merge_sort
from tabelas import calcular_metricas, imprimir_tabela


def executar_benchmark_threshold():
    n = 1_000_000
    num_workers = 4

    thresholds = [100, 1_000, 10_000, 50_000, 100_000]

    # Gera os mesmos dados para todos os testes
    gerador = random.Random(42)
    dados = [
        gerador.randint(1, 10_000_000)
        for _ in range(n)
    ]

    # Executa a versão sequencial como referência
    inicio = time.perf_counter()
    resultado_seq = merge_sort_seq(dados.copy())
    tempo_serial = time.perf_counter() - inicio

    resultados = []
    melhor_threshold = None
    menor_tempo = float("inf")

    print("\n=== BENCHMARK DE THRESHOLD - MERGESORT ===")
    print(f"Elementos: {n:,}")
    print(f"Processos: {num_workers}")
    print(f"Tempo sequencial: {tempo_serial:.4f} s")

    for threshold in thresholds:
        print(f"\nTestando Threshold = {threshold:,}...")

        inicio = time.perf_counter()

        resultado_par = parallel_merge_sort(
            dados.copy(),
            num_workers=num_workers,
            threshold=threshold
        )

        tempo_paralelo = time.perf_counter() - inicio

        # Valida a ordenação
        assert resultado_par == resultado_seq, (
            "Erro na ordenação!"
        )

        speedup, eficiencia = calcular_metricas(
            tempo_serial,
            tempo_paralelo,
            num_workers
        )

        quantidade_blocos = math.ceil(n / threshold)

        resultados.append([
            f"{threshold:,}",
            f"{quantidade_blocos:,}",
            f"{tempo_paralelo:.4f}",
            f"{speedup:.2f}x",
            f"{eficiencia:.2f}%"
        ])

        if tempo_paralelo < menor_tempo:
            menor_tempo = tempo_paralelo
            melhor_threshold = threshold

    imprimir_tabela(
        "RESULTADOS - ANALISE DE THRESHOLD",
        [
            "Threshold",
            "Blocos",
            "Tempo (s)",
            "Speedup",
            "Eficiencia"
        ],
        resultados
    )

    print(f"\nMelhor Threshold medido: {melhor_threshold:,}")
    print(f"Menor tempo paralelo: {menor_tempo:.4f} s")
    print("\nTodos os resultados foram validados!")


if __name__ == "__main__":
    executar_benchmark_threshold()
