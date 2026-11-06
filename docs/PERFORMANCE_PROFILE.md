# Perfil de desempenho Android — Mikael Runtime 8

## Alteração implementada nesta branch

A branch `perf/android-parallel-gc` adiciona um patch pequeno ao HotSpot 8:

- Em builds Android (`__ANDROID__`), quando o HotSpot ainda não recebeu uma escolha explícita de coletor, a ergonomia seleciona `UseParallelGC`.
- Fora do Android, a lógica original de seleção de coletor permanece inalterada.
- Opções explícitas do usuário, como `-XX:+UseG1GC`, `-XX:+UseSerialGC` ou `-XX:+UseParallelGC`, continuam tendo precedência porque `select_gc()` só chama a seleção ergonômica quando nenhum coletor foi selecionado.
- Não fixa `ParallelGCThreads`: o HotSpot continua dimensionando as threads de acordo com o ambiente.

## Por que esta escolha

O perfil pedido prioriza throughput. O Parallel GC é o coletor de throughput do HotSpot; ele pode reduzir o custo de coleta por unidade de trabalho em cargas multi-core, mas usa pausas stop-the-world. Portanto, não há garantia de FPS maior nem de menos stutter em todos os modpacks.

G1 foi projetado para metas de latência e tende a fazer mais sentido em heaps maiores; a documentação Java 8 o recomenda para heaps grandes, aproximadamente 6 GB ou mais, com requisitos de latência. Isso não descreve bem o telefone Android de memória limitada usado no primeiro teste. A escolha do Parallel GC é uma hipótese de desempenho a ser medida no aparelho, não uma promessa.

## Testes necessários

### Build/CI

1. Verificar hash do patch.
2. Aplicar o patch ao commit fixado do OpenJDK com `git apply --check`.
3. Compilar HotSpot Server AArch64.
4. Empacotar a runtime e validar o formato MultiRT e ELF64/AArch64.

### Teste no Android

Comparar a versão anterior com a versão desta branch no mesmo aparelho e no mesmo mundo já gerado. Manter iguais resolução, distância de renderização, mods, opções gráficas e limite de memória.

Registrar:
- FPS médio e quedas perceptíveis;
- memória usada e heap máximo;
- mensagens/pausas de GC;
- atrasos do servidor integrado;
- temperatura/limitação térmica, se o launcher disponibilizar essa informação;
- estabilidade por pelo menos 20–30 minutos.

Para diagnóstico temporário, pode-se acrescentar:
```
-XX:+PrintGCDetails -XX:+PrintGCTimeStamps
```
Essas opções geram logs e não devem ser usadas na comparação de FPS final, pois a escrita de logs adiciona sobrecarga. Removê-las depois do diagnóstico.

### Critério de aceitação

Manter o novo padrão somente se o build passar e a comparação no aparelho mostrar ganho reproduzível de throughput sem regressão inaceitável de pausas, stutter, memória ou estabilidade. Se as pausas piorarem, reverter o padrão e manter o coletor selecionável manualmente.

## Limites

Esta alteração afeta a seleção ergonômica do coletor de lixo. Não altera o JIT, o renderer GL4ES, drivers, geração de chunks ou a carga de mods. Não é possível inferir ganho de FPS a partir de uma compilação bem-sucedida.


## Ergonomia de memória associada

A branch `memory/android-adaptive-heap`, baseada nesta, adiciona um limite conservador de 85% para `MaxHeapFreeRatio` no Parallel GC Android, somente quando o usuário não definiu esse valor. O objetivo é permitir encolhimento após picos de alocação. O trade-off e os testes estão em [MEMORY_PROFILE.md](MEMORY_PROFILE.md); não assumir ganho sem benchmark.

## SIMD de cópia de memória — candidato Android ARM64

A branch `perf/android-asimd-memory` acrescenta `patches/mikael_android_simd_memory.diff` em `VM_Version::get_processor_features()`:

- Em Android AArch64, consulta o bit `HWCAP_ASIMD` divulgado pelo kernel.
- Só quando ASIMD está presente e `UseSIMDForMemoryOps` ainda é padrão, ativa os stubs SIMD de movimentação de memória do HotSpot.
- Um `-XX:-UseSIMDForMemoryOps` ou `-XX:+UseSIMDForMemoryOps` explícito é preservado.
- Fora do Android, a seleção original do OpenJDK permanece.

Os stubs AArch64 já têm caminhos SIMD e não SIMD. O objetivo é testar cópias grandes e movimentação de arrays em Java, trabalho que pode aparecer durante carregamento de chunks, serialização e execução de mods. A hipótese é reduzir instruções e melhorar throughput de cópia; o efeito em FPS depende do gargalo real e pode ser neutro ou regressivo em alguns SoCs.

**Não é um ajuste de renderização:** não modifica PowerVR, OpenGL ES, GL4ES, LWJGL, shaders, OptiFine ou a GPU. Não declarar aumento de FPS antes do benchmark no mesmo mundo, resolução, render distance, heap e conjunto de mods.

Plano, requisitos de CPU e teste: [ANDROID_SIMD_PROFILE.md](ANDROID_SIMD_PROFILE.md).


## Ajuste nativo para Cortex-A53

A branch `perf/android-cortex-a53-native-tune` acrescenta **-mtune=cortex-a53** à compilação C/C++ do JDK/HotSpot somente no alvo AArch64 Android.

- O Galaxy A12 SM-A125M usa o MediaTek Helio P35 com núcleos Cortex-A53.
- `-mtune` altera o escalonamento de instruções para esse núcleo; não é `-mcpu` nem `-march`, portanto não aumenta a ISA mínima exigida do runtime.
- Pode ajudar código nativo do HotSpot e bibliotecas do JDK (por exemplo, operações de ZIP e inicialização nativa), mas não altera a geração de código Java feita pelo compilador JIT C2.
- O possível efeito em FPS e no tempo de carregamento é limitado e precisa ser medido no aparelho; não há ganho presumido.

### Inicialização do Minecraft

O build é HotSpot Server. A compilação em camadas (Tiered Compilation) já é o modo padrão da Server VM no Java 8, combinando compilação inicial mais rápida com otimização posterior. Forçá-la novamente não acrescentaria benefício. O CDS clássico do Java 8 é documentado como restrito à Client VM e ao Serial GC, combinação diferente desta runtime Server/Parallel GC; não habilitar `-Xshare:on` sem um arquivo de classes compatível.

Não foram usados `-Xverify:none`, `-Xcomp` ou limites de compilação agressivos: eles podem reduzir verificações de bytecode, aumentar muito o trabalho de compilação durante a abertura ou piorar travamentos na primeira partida. A maior parte da abertura de um modpack Forge também depende de varredura de JARs, inicialização dos mods, leitura de configurações e criação de recursos; a JVM sozinha não controla essas etapas.

**Validação necessária:** comparar a branch anterior e a branch A53 no mesmo aparelho, com o mesmo conjunto de mods e mundo, cronometrando do toque em Jogar até o menu/mundo e registrando FPS/frametime depois de aquecer. Manter o ajuste somente se houver melhoria repetível sem regressão.
