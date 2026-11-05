# Perfil de memória Android — Mikael Runtime 8

## Objetivo

Reduzir a memória Java comprometida que permanece ociosa depois de picos de alocação, sem impor um heap máximo fixo nem alterar limites escolhidos pelo launcher/usuário.

## Alteração no HotSpot

O patch `mikael_android_adaptive_heap.diff` modifica somente a ergonomia do Parallel GC em builds Android:

- Se `UseAdaptiveSizePolicy` estiver ativo e `MaxHeapFreeRatio` não tiver sido definido explicitamente, o padrão Android passa de 100 para 85.
- Fora do Android, o valor original 100 é mantido.
- Se o usuário/launcher informar `-XX:MaxHeapFreeRatio=N`, o valor explícito é preservado.
- O ajuste não define `-Xms`, `-Xmx`, `MaxRAM`, `MinHeapFreeRatio`, nem o número de threads do GC.
- O patch só afeta o caminho `set_parallel_gc_flags()`; não altera Serial GC ou G1.

## Efeito esperado e trade-off

No Parallel Scavenge, `MaxHeapFreeRatio` participa do cálculo de espaço livre alvo após coleta principal. O valor 85 permite que o heap adaptativo encolha quando a fração livre ultrapassa aproximadamente 85% do espaço vivo relevante, em vez de usar 100% e deixar essa regra sem limite superior.

A intenção é recuperar espaço ocioso depois de picos, não reduzir o heap durante carga normal. Ainda assim, encolher o heap pode causar novo crescimento e mais trabalho de GC se a carga voltar rapidamente. Por isso, 85 é uma hipótese conservadora para teste, não uma garantia de menor RSS ou maior FPS.

A alteração não controla memória nativa de LWJGL/GL4ES, bibliotecas JNI, buffers diretos, texturas ou o consumo do próprio Android. Ela também não substitui a configuração de heap feita pelo CS Launcher Plus.

## Regressão coberta

O teste automatizado valida:
- hash fixo do patch;
- guarda `__ANDROID__`;
- padrão Android 85;
- padrão não Android 100;
- condição `FLAG_IS_DEFAULT`, preservando valor explícito;
- inclusão do patch no bloco estrito de aplicação.

O build também executa `git apply --check` contra o commit fixado do OpenJDK antes de aplicar o patch.

## Validação no Galaxy A12

Comparar runtime base e branch de memória com:
- mesmo limite `-Xmx` configurado no launcher;
- mesmo mundo já gerado, resolução, render distance e conjunto de mods;
- uma sessão de 20–30 minutos com exploração e outra após carregar/descarregar áreas;
- RSS/PSS do processo, heap usado/máximo, GC count/time, FPS médio e stutter.

Fazer ao menos três execuções por versão, alternando a ordem para reduzir viés térmico. Separar logs com `-XX:+PrintGCDetails -XX:+PrintGCTimeStamps` dos testes de FPS, pois logging adiciona sobrecarga.

**Critério:** manter o padrão somente se reduzir memória retida após picos sem piorar throughput, pausas, stutter ou estabilidade de forma relevante. Se aumentar churn de GC ou piorar FPS, reverter o padrão para 100 e manter o controle manual.

## Limites

Nenhum ganho de RAM ou FPS foi declarado antes da medição no dispositivo. A compilação ARM64 e o teste real no launcher são etapas obrigatórias antes de recomendar a branch para uso diário.
