# Estado da compilação da runtime

## Situação verificada

A primeira pipeline de compilação própria foi adicionada em .github/workflows/build-mikael-runtime8-arm64.yml. **Ainda não há evidência de uma JVM/JRE compilada nem artifact de runtime.** O estado só muda depois de uma execução real e da validação do pacote.

## Pipeline ARM64 criada

O workflow Build Mikael Runtime 8 ARM64 usa Ubuntu 22.04 e JDK 8 de bootstrap. Ele:

1. Busca a receita MojoLauncher em commit imutável.
2. Confere os hashes dos três patches Android ARM64.
3. Fixa OpenJDK 8u, FreeType, CUPS e termux-elf-cleaner por commit.
4. Baixa NDK r10e e GCC toolchain com verificação SHA-256.
5. Remove o passo interativo tmate e substitui aplicação parcial de patches por git apply --check + aplicação fatal.
6. Compila HotSpot Server AArch64.
7. Valida bin/java, libjvm.so, metadados Java 8 e ELF64/AArch64.
8. Empacota um .tar.xz no formato MultiRT do CS Launcher Plus e gera SHA-256/manifesto.

Detalhes dos pinos e limitações: [ARM64_REAL_BUILD.md](ARM64_REAL_BUILD.md).

## Outras pré-verificações

- .github/workflows/openjdk8-arm64-preflight.yml: confere fonte OpenJDK 8u e aplicação sequencial dos patches principais.
- .github/workflows/audit-mojo-openjdk8.yml: confere commit/blob da receita Mojo e registra riscos estáticos, sem executar o build.
- scripts/audit_openjdk8_recipe.py: auditoria da receita histórica.
- scripts/audit_mojo_openjdk8_recipe.py: auditoria da receita mantida pelo Mojo.

## Kit de diagnóstico para teste no celular

O workflow .github/workflows/build-test-kit.yml compila um JAR de diagnóstico Java 8. O kit não contém JVM/JRE; só testa a runtime usada para executá-lo.

## Critérios restantes após o build

1. Confirmar build verde e artifact .tar.xz gerado.
2. Conferir dependências ELF e símbolos Android/Bionic.
3. Executar java -version, smoke tests, JNI, threads e GC no Android 12 real.
4. Testar instalação/seleção no FCL e CS Launcher Plus.
5. Testar Minecraft 1.12.2 Vanilla, Forge 14.23.5.2864, OptiFine HD U G5 e modpack.

Nenhum APK foi gerado. Nenhum artefato de diagnóstico ou pacote de terceiros será anunciado como Mikael Runtime 8.
