# Estado da Mikael Runtime 8

## Situação verificada em 2026-11-05

**Build real concluído e runtime executada no Android 12 ARM64.**

A pipeline Build Mikael Runtime 8 ARM64 gerou o artefato MultiRT `Mikael-Runtime-8-Android-ARM64` em formato `.tar.xz`, com manifesto e SHA-256. O pacote foi importado no CS Launcher Plus e a JVM iniciou Minecraft 1.12.2.

## Teste real no aparelho

O `latest.log` enviado confirma:

- OpenJDK 64-Bit Server VM 1.8.0_512-internal em Linux/aarch64/Android 12.
- Forge 14.23.5.2860.
- OptiFine 1.12.2 HD U G5.
- LWJGL 2.9.4 e GL4ES 1.1.5.
- ProjectE, Simple Storage Network e ProjectE Storage Bridge carregados.
- Mundo singleplayer aberto, servidor integrado iniciado e mundo salvo no encerramento.
- Nenhum crash fatal da JVM aparece no trecho fornecido.

**Limites:** o teste foi curto; não prova estabilidade prolongada, ganho de FPS, compatibilidade com todos os mods nem teste com Forge 14.23.5.2864.

## Problemas observados e responsáveis

1. **JNA/Narrator:** o JNA tentou carregar uma biblioteca nativa temporária em `/storage/emulated/0/CS LAUNCHER PLUS/.cache/JNA/temp`. O Android bloqueou esse caminho no linker namespace. A correção deve colocar o diretório temporário de JNA no armazenamento privado do aplicativo. Se o launcher aceitar argumento JVM, testar `-Djna.tmpdir=/data/user/0/com.craftstudio.cslauncher/cache`; confirmar no próximo log. É configuração do launcher/JNA, não uma correção comprovada no HotSpot.
2. **Atrasos do servidor integrado:** foram registrados 2667 ms e 3091 ms de atraso durante o carregamento inicial. A causa ainda não foi isolada. Medir FPS, heap, GC e repetir em mundo já gerado antes de alterar flags.
3. **OpenGL/GL4ES:** VboRegions não está disponível porque o backend reporta ausência de OpenGL 1.3/ARB_copy_buffer. Shaders também foram bloqueados pelo Fast Render. São limitações/configurações gráficas, não falhas da JVM.
4. **ProjectE:** avisos EMC Exploit e fluidos ausentes pertencem às receitas/registro de fluidos dos mods. Não modificar a JVM para tentar corrigir esses avisos.
5. **Forge:** o teste executou 2860; ainda falta uma execução separada com 14.23.5.2864.

Relatório completo: [ANDROID_TEST_LOG_2026-11-05.md](ANDROID_TEST_LOG_2026-11-05.md).

## Perfil base GC + memória — build ARM64 concluído

A branch `memory/android-adaptive-heap` contém os patches Android-only para selecionar Parallel GC por ergonomia e usar `MaxHeapFreeRatio=85` apenas quando o valor ainda é padrão. Opções explícitas permanecem respeitadas.

- CI run [42128441200](https://github.com/mikael8367/Mikael-Runtime-8/actions/runs/42128441200): sucesso em compilação, validação/empacotamento e upload.
- Artefato `Mikael-Runtime-8-Android-ARM64`, ID `13463891035`, com SHA-256 `a02fe616eeb7af27409c06dd0106ffc092c07d0cbd4334857b72cb5882d2ffbf`.
- A aprovação do build comprova compilação e integridade estrutural; não comprova ganho de FPS nem estabilidade prolongada no aparelho.

## Perfil SIMD — nova validação pendente

A branch `perf/android-asimd-memory` adiciona `patches/mikael_android_simd_memory.diff`: em Android AArch64, ativa `UseSIMDForMemoryOps` somente se `HWCAP_ASIMD` estiver disponível e o usuário não tiver definido a flag explicitamente. O patch será submetido a teste de hash, contagem dos hunks, aplicação estrita ao OpenJDK fixado, build ARM64, inspeção ELF e empacotamento. Depois, precisa de comparação real de FPS e stutter no aparelho. Detalhes: [ANDROID_SIMD_PROFILE.md](ANDROID_SIMD_PROFILE.md).

## Pipeline ARM64

O workflow usa Ubuntu 24.04 e JDK 8 de bootstrap. Ele fixa a receita MojoLauncher, OpenJDK 8u, patches, FreeType, CUPS, NDK r10e, GCC toolchain e termux-elf-cleaner; aplica patches estritamente, compila HotSpot Server AArch64, valida ELF64/AArch64 e empacota o formato MultiRT.

Detalhes: [ARM64_REAL_BUILD.md](ARM64_REAL_BUILD.md).

## Próximos critérios de validação

- [ ] JNA extrair/carregar sua biblioteca a partir de diretório privado do aplicativo.
- [ ] Testar Forge 14.23.5.2864.
- [ ] Medir FPS, heap e pausas de GC em condições repetíveis.
- [ ] Sessão de 20–30 minutos sem crash, acompanhando memória.
- [ ] Auditar EMC e fluidos no conjunto de mods.
- [ ] Guardar o próximo latest.log completo e crash report, se houver.

Nenhum APK foi gerado.


## Perfil de memória — branch em validação

A branch `memory/android-adaptive-heap` parte de `perf/android-parallel-gc` e adiciona `patches/mikael_android_adaptive_heap.diff`: Android + Parallel GC usa `MaxHeapFreeRatio=85` apenas quando `FLAG_IS_DEFAULT` é verdadeiro; plataformas não Android mantêm 100 e valores explícitos são preservados. O patch não fixa `-Xmx`, `-Xms` ou threads. Testes de regressão verificam o hash e essas condições. Build ARM64 e benchmark de RSS/PSS, heap, GC, FPS e stutter ainda são necessários. Detalhes: [MEMORY_PROFILE.md](MEMORY_PROFILE.md).
