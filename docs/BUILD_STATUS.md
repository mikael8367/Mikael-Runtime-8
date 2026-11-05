# Estado da compilação da runtime

## Situação verificada

Ainda não existe binário JVM/JRE produzido neste repositório. O pipeline atual valida documentação e configuração; ele não tenta compilar OpenJDK nem gera artefatos de runtime.

## Candidato histórico

O projeto PojavLauncherTeam/android-openjdk-build-multiarch, branch buildjre8, documenta uma rota OpenJDK 8 para Android AArch64. O próprio projeto foi arquivado em 19/05/2025 e sua documentação exige Android NDK r10e, alertando que outras versões do NDK causam erros de compilação.

Referências:
- https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch
- https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/blob/buildjre8/README.md

## Pipeline inicial de ARM64

Foi adicionado `.github/workflows/openjdk8-arm64-preflight.yml` para validar, com SHAs fixos, a combinação de OpenJDK 8u e patches Android. Esta etapa é uma pré-verificação de fonte e patches; **não compila JVM/JRE**. Ela impede que falhas de aplicação de patches sejam ignoradas. O plano e os critérios de liberação do build completo estão em [OPENJDK8_ARM64_BUILD.md](OPENJDK8_ARM64_BUILD.md).

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

## Próxima entrega técnica

A próxima etapa é corrigir os achados prioritários em uma cópia controlada dos patches, revisar licenças/proveniência e só então preparar um build reproduzível. Só depois disso deve ser criado um workflow de build e publicação de artefatos. Nenhum APK será gerado sem pedido explícito.


## Kit de diagnóstico para teste no celular

Foi adicionado `tests/device-smoke/` com um programa Java 8 e o workflow `.github/workflows/build-test-kit.yml`. O workflow compila o JAR de diagnóstico e publica um ZIP por 30 dias em GitHub Actions. Esse pacote não contém JVM/JRE e não é instalável como runtime; ele permite testar uma JRE Java 8 ARM64 já disponível no aparelho e coletar um primeiro relatório.

A Mikael Runtime 8 própria continua sem binário. Não publicar o kit como se fosse a runtime.
