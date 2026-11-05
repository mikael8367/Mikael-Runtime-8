# Perfil SIMD de memória — Mikael Runtime 8

## Alteração

A branch `perf/android-asimd-memory` adiciona o patch `mikael_android_simd_memory.diff` ao OpenJDK 8u fixado.

No HotSpot AArch64, `UseSIMDForMemoryOps` seleciona stubs de cópia de memória que usam registradores SIMD. O padrão upstream é falso; a alteração:

1. Lê `AT_HWCAP` por `getauxval`.
2. Verifica `HWCAP_ASIMD` (bit 1, com definição de compatibilidade caso o header antigo do NDK não a forneça).
3. Em builds Android, ativa a flag apenas se ASIMD estiver presente e `FLAG_IS_DEFAULT(UseSIMDForMemoryOps)` continuar verdadeiro.
4. Mantém `-XX:+UseSIMDForMemoryOps` e `-XX:-UseSIMDForMemoryOps` explícitos do usuário/launcher.

A alteração não força SIMD em processadores cujo kernel não anuncia esse recurso e não altera o comportamento não Android.

## Por que testar

O código AArch64 do HotSpot 8 possui caminhos distintos de cópia: um caminho usa pares de registradores gerais; o outro usa operações SIMD de 128 bits. Os stubs são usados em movimentação de memória da JVM e podem beneficiar operações de array/cópia do runtime, que aparecem em cargas de jogos e mods.

O ganho esperado é somente uma hipótese de throughput de memória. Não há resultado de benchmark ainda. O desempenho pode variar por microarquitetura; a flag deve ser revertida se o teste no aparelho mostrar regressão.

## Limites

Esta mudança não otimiza diretamente:
- GPU PowerVR GE8320;
- OpenGL ES, GL4ES ou LWJGL;
- draw calls, shaders, VBO ou configurações de OptiFine;
- lógica interna dos mods, geração de chunks ou rede.

Se o FPS estiver limitado pelo renderer/driver ou pela GPU, a diferença da JVM poderá ser pequena ou imperceptível.

## Validação de build

- [ ] Hash Git blob do patch validado.
- [ ] Contagem dos hunks unified diff validada.
- [ ] Aplicação estrita com `git apply --check` no OpenJDK fixado.
- [ ] Build HotSpot Server AArch64 concluído.
- [ ] `java` e `libjvm.so` validados como ELF64/AArch64.
- [ ] Pacote MultiRT criado e checksum registrado.

## Benchmark no Android

Comparar a build base `memory/android-adaptive-heap` e a nova build SIMD. Manter constantes o mesmo aparelho, mundo já gerado, resolução, render distance, mods, configurações gráficas e `-Xmx`.

1. Aquecer cada execução por 5 minutos.
2. Fazer pelo menos três execuções de 20–30 minutos por build, alternando a ordem para reduzir viés térmico.
3. Registrar FPS médio, quedas/stutter, heap usado, RSS/PSS, GC count/time e temperatura/thermal throttling quando disponível.
4. Fazer uma segunda comparação explorando chunks e carregando/descarregando áreas.
5. Não usar logs detalhados de GC durante a medição final de FPS.

**Critério:** manter SIMD como padrão somente se o ganho for repetível e não aumentar stutter, consumo de memória ou instabilidade. Comparar mediana entre execuções, não um único pico de FPS.

Para diagnóstico de code cache, `-XX:+PrintCodeCache` pode ajudar a verificar ocupação; remover opções de diagnóstico antes do benchmark final.
