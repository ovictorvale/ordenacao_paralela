# Laboratório 03 — Ordenação Paralela

**Disciplina:** Computação Paralela e Concorrente  
**Professor:** Wellington Brito

## Objetivo

Implementei e testei algoritmos de ordenação sequencial e paralela em Python. Comparei os tempos de execução e calculei o Speedup e a Eficiência para observar quando o paralelismo foi vantajoso.

Os algoritmos trabalhados no roteiro foram **MergeSort, QuickSort, Odd-Even Transposition Sort e Bitonic Sort**. Também realizei os quatro desafios propostos.

## Ambiente

- Python 3 e Visual Studio Code.
- Bibliotecas padrão do Python, principalmente `concurrent.futures`, `multiprocessing`, `random` e `time`.
- Testes paralelos com quatro processos.

## Arquivos

| Arquivo | Finalidade |
| --- | --- |
| `mergesort_paralelo.py` | MergeSort sequencial e paralelo; teste com tamanhos diferentes. |
| `benchmark_threshold.py` | Teste de diferentes valores de Threshold no MergeSort. |
| `quicksort_paralelo.py` | QuickSort sequencial e paralelo. |
| `benchmark_pivos.py` | Comparação dos pivôs primeiro elemento e mediana de três. |
| `oddeven_sort_paralelo.py` | Comparação do Odd-Even com o MergeSort. |
| `bitonic_sort_paralelo.py` | Bitonic Sort sequencial e paralelo. |
| `bucket_sort_paralelo.py` | Bucket Sort com quatro faixas de transações financeiras. |
| `benchmark_carga_ociosa.py` | Medição de trabalho e espera dos processos no MergeSort. |
| `tabelas.py` | Exibição das tabelas e cálculo das métricas. |

## Execução

Na pasta do projeto, execute os arquivos pelo terminal:

```powershell
python mergesort_paralelo.py
python benchmark_threshold.py
python quicksort_paralelo.py
python benchmark_pivos.py
python oddeven_sort_paralelo.py
python bitonic_sort_paralelo.py
python bucket_sort_paralelo.py
python benchmark_carga_ociosa.py
```

O teste do Odd-Even foi feito com **50.000 elementos**, conforme o desafio do roteiro, e pode demorar alguns minutos.

## Métricas

- **Speedup:** tempo sequencial dividido pelo tempo paralelo (`S = Tseq / Tpar`).
- **Eficiência:** Speedup dividido pelo número de processos, multiplicado por 100 (`E = S / P × 100`).
- **Threshold:** tamanho usado para definir como o trabalho de ordenação é dividido na implementação do MergeSort.

## Resultados e análise

No MergeSort, o paralelismo foi mais lento para 10.000 e 100.000 elementos e mais rápido para 500.000 e 2.000.000. No teste com 1 milhão de elementos, os menores tempos foram obtidos com Thresholds de 50.000 e 100.000.

No QuickSort, a **mediana de três** dividiu melhor as tarefas do que o **primeiro elemento** em uma entrada parcialmente ordenada. No Odd-Even, as várias comparações entre vizinhos e as sincronizações deixaram o algoritmo bem mais lento que o MergeSort. No Bitonic Sort, a execução paralela não superou a sequencial no vetor de 8.192 elementos.

No Bucket Sort, os quatro baldes ficaram com quantidades próximas de elementos, mas a execução paralela foi mais lenta devido ao custo de criação e comunicação dos processos. Na medição da carga ociosa do MergeSort, registrei o tempo de espera na barreira de sincronização dos trabalhadores.

**As tabelas com os valores medidos e as respostas aos desafios estão no relatório do laboratório.**
