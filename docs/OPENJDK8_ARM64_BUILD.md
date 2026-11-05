# Etapa de compilação OpenJDK 8 ARM64

## Objetivo

Preparar uma JRE Java 8 Android `arm64-v8a` para a Mikael Runtime 8. O alvo inicial é Minecraft Java 1.12.2; compatibilidade com Forge, OptiFine, mods e modpacks só será declarada após testes no Android.

## Base atual sob investigação

O candidato prioritário passou a ser o fork ativo [MojoLauncher/android-openjdk-build-multiarch](https://github.com/MojoLauncher/android-openjdk-build-multiarch), commit observado `a0d811b6c5ebd251374751438ec8b635f0746ab4`. Ele possui workflow AArch64 e publicação de JRE 8 de referência. A revisão completa está em [MOJO_OPENJDK8_RECIPE_REVIEW.md](MOJO_OPENJDK8_RECIPE_REVIEW.md).

O fork atualiza a receita histórica, mas ainda mantém pontos que bloqueiam a execução direta: patches com `--reject` e falhas toleradas, clone OpenJDK sem SHA, downloads de dependências/toolchain sem checksum, NDK r10e sem provisionamento explícito visível no workflow, ferramenta elf-cleaner por tag e tmate no CI. O workflow [Audit maintained OpenJDK 8 ARM64 recipe](../.github/workflows/audit-mojo-openjdk8.yml) verifica a identidade dos scripts e relata esses riscos sem executá-los.

## Pré-verificação de fonte e patches

O workflow [OpenJDK 8 ARM64 source preflight](../.github/workflows/openjdk8-arm64-preflight.yml) continua verificando o commit OpenJDK 8u e aplicação sequencial dos patches Android. Essa etapa não compila JVM/JRE.

## Critérios para liberar o build completo

- [ ] Fixar a receita e todos os scripts por commit/blob SHA.
- [ ] Fixar o commit exato do OpenJDK 8u.
- [ ] Provisionar NDK r10e explicitamente e validar SHA-256 oficial do NDK, FreeType, CUPS e GCC toolchain.
- [ ] Substituir aplicação de patch tolerante por `git apply --check` + aplicação fatal.
- [ ] Remover tmate e qualquer execução interativa do CI.
- [ ] Reproduzir a toolchain histórica em ambiente isolado.
- [ ] Compilar HotSpot Server AArch64 e bibliotecas Java.
- [ ] Verificar ELF64/AArch64, ABI Android, API mínima, símbolos Bionic e dependências dinâmicas.
- [ ] Empacotar JRE no formato aceito pelo launcher, com manifesto de proveniência, licenças e SHA-256.
- [ ] Executar `java -version`, smoke tests, JNI, threads, GC e carregamento de bibliotecas no Android real.
- [ ] Testar Minecraft 1.12.2 Vanilla, Forge, OptiFine, Forge+OptiFine e modpack.

## Limites

Um build verde de CI não prova execução no telefone. A JVM também não fornece LWJGL, GL4ES, assets, classpath ou loader de mods; esses componentes continuam sob responsabilidade do launcher e do ambiente gráfico.

Nenhum APK é produzido nesta etapa.
