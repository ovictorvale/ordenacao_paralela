
import random
import time
from concurrent.futures import ProcessPoolExecutor

from tabelas import calcular_metricas, imprimir_tabela


# Distribui os valores entre os quatro baldes
def distribuir_baldes(vetor):
    baldes = [[], [], [], []]

    for valor in vetor:
        if not 0 <= valor <= 1000:
            raise ValueError("Valor fora da faixa permitida!")

        indice = min(int(valor // 250), 3)
        baldes[indice].append(valor)

    return baldes


# Ordena os elementos de um balde
def ordenar_balde(balde):
    return sorted(balde)


# Bucket Sort Sequencial
def bucket_sort_seq(vetor):
    baldes = distribuir_baldes(vetor)

    resultado = []

    for balde in baldes:
        resultado.extend(ordenar_balde(balde))

    return resultado


# Bucket Sort Paralelo
def bucket_sort_paralelo(vetor, num_workers=4):
    if num_workers < 1:
        raise ValueError("Numero de processos invalido!")

    baldes = distribuir_baldes(vetor)

    # Ordena os baldes em processos separados
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        baldes_ordenados = list(
            executor.map(ordenar_balde, baldes)
        )

    # Reune os baldes na ordem correta
    resultado = []

    for balde in baldes_ordenados:
        resultado.extend(balde)

    return resultado


# Benchmark
def executar_benchmark():
    n = 1_000_000
    num_workers = 4

    gerador = random.Random(42)

    # Simula um milhao de transacoes financeiras
    dados = [
        round(gerador.uniform(0, 1000), 2)
        for _ in range(n)
    ]

    print("\n=== BUCKET SORT SEQUENCIAL VS PARALELO ===")
    print(f"Elementos: {n:,}")
    print(f"Processos: {num_workers}")
    print("Faixa de valores: R$ 0,00 a R$ 1.000,00")

    # Execucao sequencial
    inicio = time.perf_counter()

    resultado_seq = bucket_sort_seq(dados)

    tempo_serial = time.perf_counter() - inicio

    # Execucao paralela
    inicio = time.perf_counter()

    resultado_par = bucket_sort_paralelo(
        dados,
        num_workers=num_workers
    )

    tempo_paralelo = time.perf_counter() - inicio

    # Valida os resultados
    assert resultado_seq == resultado_par == sorted(dados), (
        "Erro: resultados da ordenacao diferentes!"
    )

    # Calcula Speedup e Eficiencia
    speedup, eficiencia = calcular_metricas(
        tempo_serial,
        tempo_paralelo,
        num_workers
    )

    # Calcula a reducao percentual do tempo
    reducao = (
        (tempo_serial - tempo_paralelo) / tempo_serial
    ) * 100

    if tempo_paralelo < tempo_serial:
        situacao = "Paralelo mais rapido"
    elif tempo_paralelo > tempo_serial:
        situacao = "Paralelo mais lento"
    else:
        situacao = "Tempos iguais"

    # Tabela principal
    imprimir_tabela(
        "RESULTADOS - BUCKET SORT",
        [
            "N",
            "Serial (s)",
            "Paralelo (s)",
            "Speedup",
            "Eficiencia",
            "Reducao (%)",
            "Situacao"
        ],
        [[
            f"{n:,}",
            f"{tempo_serial:.4f}",
            f"{tempo_paralelo:.4f}",
            f"{speedup:.2f}x",
            f"{eficiencia:.2f}%",
            f"{reducao:+.2f}%",
            situacao
        ]]
    )

    # Analisa a quantidade de elementos por balde
    baldes = distribuir_baldes(dados)

    faixas = [
        "0 a 250",
        "250 a 500",
        "500 a 750",
        "750 a 1000"
    ]

    distribuicao = []

    for i, balde in enumerate(baldes):
        percentual = (len(balde) / n) * 100

        distribuicao.append([
            f"Balde {i + 1}",
            faixas[i],
            f"{len(balde):,}",
            f"{percentual:.2f}%"
        ])

    imprimir_tabela(
        "DISTRIBUICAO DAS TRANSACOES",
        [
            "Balde",
            "Faixa (R$)",
            "Elementos",
            "Percentual"
        ],
        distribuicao
    )

    print("\nTodos os resultados foram validados!")


if __name__ == "__main__":
    executar_benchmark()
