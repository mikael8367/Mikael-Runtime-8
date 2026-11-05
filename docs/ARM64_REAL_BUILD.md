# Build ARM64 real da Mikael Runtime 8

O workflow \`.github/workflows/build-mikael-runtime8-arm64.yml\` compila uma JRE Java 8 Android ARM64 usando a receita MojoLauncher auditada, mas não executa diretamente os scripts upstream sem alterações.

## O que o pipeline faz

1. Usa runner Ubuntu 22.04 e JDK 8 de bootstrap.
2. Busca a receita MojoLauncher no commit imutável \`a0d811b6c5ebd251374751438ec8b635f0746ab4\`.
3. Verifica os hashes dos patches Android usados.
4. Reescreve os scripts de aquisição para fixar OpenJDK 8u, FreeType, CUPS, GCC toolchain e termux-elf-cleaner.
5. Baixa NDK r10e do domínio oficial do Android e confere SHA-256 antes de extrair.
6. Aplica os patches em sequência com \`git apply --check\`, falha fatal e \`git diff --check\`.
7. Compila HotSpot Server AArch64 e gera a JRE.
8. Verifica o pacote pelo contrato MultiRT do CS Launcher Plus, incluindo \`bin/java\`, \`libjvm.so\`, metadados Java 8 e ELF64/AArch64.
9. Produz \`Mikael-Runtime-8-Android-ARM64.tar.xz\`, SHA-256, manifesto e relatórios ELF.

## Pinos de proveniência

- Receita MojoLauncher: \`a0d811b6c5ebd251374751438ec8b635f0746ab4\`.
- OpenJDK 8u: \`b661ee6ff840d6922aa7424a4d8f24760b21cf26\`.
- FreeType 2.10.4: \`6a2b3e4007e794bfc6c91030d0ed987f925164a8\`.
- CUPS 2.2.4: \`070e33a4c9dfdb21638de0fedb2904391c30d070\`.
- GCC 13 ARM64 toolchain: SHA-256 \`ad32f8952dc2bbe5d9e7a6f4a6f0a185a8b1dfbe6f0e7410db5da8ba45f3453f\`.
- Android NDK r10e Linux x86_64: SHA-256 \`ee5f405f3b57c4f5c3b3b8b5d495ae12b660e03d2112e4ed5c728d349f1e520c\`.
- termux-elf-cleaner: \`d08dfdc73ff5b6061e134b90bec16489655015f5\`.

## Critérios de conclusão

Um artifact só será produzido se o build terminar e o empacotador validar a estrutura e os cabeçalhos ELF. Isso ainda não prova execução no Android 12. O binário precisa ser testado no aparelho, incluindo \`java -version\`, JNI, GC, threads, FCL, CS Launcher Plus, Forge 1.12.2 e OptiFine HD U G5.

O pipeline não publica releases, não gera APK e não declara ganho de FPS. O artefato é disponibilizado na seção Artifacts da execução do GitHub Actions.
