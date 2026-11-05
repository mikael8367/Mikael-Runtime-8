# Estado da compilação da runtime

## Situação verificada

Ainda não existe binário JVM/JRE produzido neste repositório. O pipeline atual valida código auxiliar, documentação, configuração, identidade de fontes/patches e kit de diagnóstico; não compila OpenJDK nem gera runtime instalável.

## Nova referência de compilação localizada

Foi identificado o fork ativo `MojoLauncher/android-openjdk-build-multiarch`, commit observado `c213846ff125eccf43e6be4adf827e42c579c4ab`. Ele contém workflow de compilação OpenJDK 8 para AArch64 e publica um pacote JRE 8 de referência. Detalhes e riscos em [MOJO_OPENJDK8_RECIPE_REVIEW.md](MOJO_OPENJDK8_RECIPE_REVIEW.md).

A receita ainda tolera falhas de patch, clona OpenJDK sem SHA, baixa NDK e dependências sem verificação SHA-256 e inicia tmate no CI. A auditoria automatizada foi adicionada, mas não executa esses scripts. Portanto, a descoberta não libera o build completo.

## Pré-verificação e auditorias

- `.github/workflows/openjdk8-arm64-preflight.yml`: confere fonte OpenJDK 8u e aplicação sequencial dos patches principais.
- `.github/workflows/audit-mojo-openjdk8.yml`: confere o commit/blob da receita Mojo e registra riscos estáticos, sem executar o build.
- `scripts/audit_openjdk8_recipe.py`: auditoria da receita histórica.
- `scripts/audit_mojo_openjdk8_recipe.py`: auditoria da receita mantida pelo Mojo.

Esses workflows não compilam JVM/JRE.

## Kit de diagnóstico para teste no celular

O workflow `.github/workflows/build-test-kit.yml` compila um JAR de diagnóstico Java 8. O kit não contém JVM/JRE; só testa a runtime usada para executá-lo.

## Bloqueios para uma runtime própria válida

1. Corrigir a receita Mojo: pin do OpenJDK, checksums oficiais, patches fatais e remoção de tmate.
2. Reproduzir toolchain NDK r10e/API 21 em ambiente isolado e documentar a compatibilidade com Android 12/Bionic.
3. Compilar HotSpot Server AArch64 e bibliotecas Java.
4. Auditar ELF, símbolos, dependências dinâmicas e API mínima.
5. Empacotar JRE e manifesto com SHA-256.
6. Executar `java -version`, smoke tests e JNI no Android real.
7. Testar FCL/CS Launcher Plus, Minecraft 1.12.2, Forge, OptiFine e modpack.

Nenhum APK foi gerado. Nenhum artefato de diagnóstico ou pacote de terceiros será anunciado como Mikael Runtime 8.
