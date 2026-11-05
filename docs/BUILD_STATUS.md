# Estado da compilação da runtime

## Situação verificada

Ainda não existe binário JVM/JRE produzido neste repositório. O pipeline atual valida documentação, configuração, identidade de fonte e kit de diagnóstico; ele não compila OpenJDK nem gera artefatos de runtime.

## Candidato histórico

O projeto PojavLauncherTeam/android-openjdk-build-multiarch, branch buildjre8, documenta uma rota OpenJDK 8 para Android AArch64. O próprio projeto foi arquivado em 19/05/2025 e sua documentação exige Android NDK r10e, alertando que outras versões do NDK causam erros de compilação.

Referências:
- https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch
- https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/blob/buildjre8/README.md

## Pipeline inicial de ARM64

Foi adicionado `.github/workflows/openjdk8-arm64-preflight.yml` para validar, com SHAs fixos, a combinação de OpenJDK 8u e patches Android. Esta etapa é uma pré-verificação de fonte e patches; **não compila JVM/JRE**. O plano e os critérios de liberação do build completo estão em [OPENJDK8_ARM64_BUILD.md](OPENJDK8_ARM64_BUILD.md).

## Por que ainda não existe um workflow de compilação completa

Não é seguro criar um workflow que simplesmente baixe e execute scripts de um repositório arquivado sem antes:
1. Fixar e revisar o commit upstream exato.
2. Auditar scripts, downloads, checksums e licenças.
3. Confirmar a disponibilidade e integridade da toolchain histórica.
4. Definir um ambiente isolado compatível e reproduzir a compilação.
5. Confirmar que os binários resultantes executam no Android 12 ARM64.

O build pode ser longo e depender de toolchain antiga. Um workflow que falha ou produz artefato incompatível não representa progresso útil.

## Auditoria de código-fonte

A revisão estática inicial está registrada em [OPENJDK8_SOURCE_AUDIT.md](OPENJDK8_SOURCE_AUDIT.md). Foram identificados riscos de fonte não fixada, falhas de patch ignoradas, downloads sem hash, sessão tmate no CI e toolchain histórica. O pipeline upstream não deve ser executado diretamente antes de mitigar esses pontos.

## Revisão dos patches Android

O diff principal foi recuperado por SHA e inventariado: 207 caminhos, 58.398 linhas adicionadas e 114 removidas. Consulte [OPENJDK8_ANDROID_PATCH_REVIEW.md](OPENJDK8_ANDROID_PATCH_REVIEW.md), [OPENJDK8_PATCH_FINDINGS.md](OPENJDK8_PATCH_FINDINGS.md) e [OPENJDK8_PATCH_INVENTORY.md](OPENJDK8_PATCH_INVENTORY.md). A revisão estática encontrou pontos que bloqueiam a adoção direta, incluindo conversão de texto, coerência AWT/GLX e validação de dados de rede/caminhos nativos. Ainda não houve compilação nem testes no dispositivo.

## Auditoria automatizada da receita upstream

Foi adicionado `scripts/audit_openjdk8_recipe.py`, com testes unitários, para confirmar o commit histórico e os Git blob SHAs de 12 scripts/workflows de build. O script registra os riscos já identificados sem executar a receita: falhas de patch toleradas, clone OpenJDK sem SHA, downloads sem checksum, extração imediata do NDK, tag de ferramenta mutável e tmate no CI. O workflow de preflight gera `openjdk8-upstream-audit.txt` junto do relatório de patches.

Esta etapa melhora a rastreabilidade, mas **não remove os riscos nem libera o build**. NDK r10e e dependências ainda precisam de hashes oficiais verificados; o build upstream continua sem ser executado.

## Kit de diagnóstico para teste no celular

O workflow `.github/workflows/build-test-kit.yml` compila um JAR de diagnóstico Java 8 e publica o ZIP `MikaelRuntime8-Device-Test-Kit` por 30 dias. O programa agora registra propriedades detalhadas da JVM, testa versão/arquitetura, reflexão, threads, heap/GC, UTF-8, ZIP/JAR e diretório temporário, e tenta salvar `MikaelRuntime8-device-report.txt` no diretório de execução (com fallback para o diretório temporário).

O kit **não contém JVM/JRE**. Ele só testa a runtime que for usada para executá-lo. O guia foi atualizado para obtenção e execução pelo celular. A execução real no Android ainda não foi recebida.

## Bloqueios atuais para testar a Mikael Runtime 8 própria

1. Toolchain Android ARM64 reproduzível e dependências com hashes verificados.
2. Correção/substituição segura da receita antiga e revisão dos patches.
3. Compilação de HotSpot e bibliotecas Java em AArch64 Android.
4. Empacotamento e validação do JRE real.
5. Execução do JRE próprio no Android 12 ARM64.
6. Testes Java, JNI e Minecraft 1.12.2 com FCL e CS Launcher Plus.

Nenhum APK foi gerado. Nenhum artefato de diagnóstico deve ser anunciado como runtime.
