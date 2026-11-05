# Estado da compilação da runtime

## Situação verificada

Ainda não existe binário JVM/JRE produzido neste repositório. O pipeline atual valida documentação e configuração; ele não tenta compilar OpenJDK nem gera artefatos de runtime.

## Candidato histórico

O projeto PojavLauncherTeam/android-openjdk-build-multiarch, branch buildjre8, documenta uma rota OpenJDK 8 para Android AArch64. O próprio projeto foi arquivado em 19/05/2025 e sua documentação exige Android NDK r10e, alertando que outras versões do NDK causam erros de compilação.

Referências:
- https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch
- https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/blob/buildjre8/README.md

## Por que não existe um workflow de compilação ainda

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

A revisão parcial está em [OPENJDK8_ANDROID_PATCH_REVIEW.md](OPENJDK8_ANDROID_PATCH_REVIEW.md). Foram examinados os diffs pequenos de syscalls/Bionic, `dlvsym`, `loadavg`, AArch32 e page trap. O patch principal `jdk8u_android.diff` tem 2.383.172 bytes; a interface de leitura não disponibilizou seu conteúdo integral, então ele permanece explicitamente pendente. Não foi feita aprovação de GC, JIT, JNI, Java2D ou compatibilidade geral.

## Próxima entrega técnica

A próxima etapa é uma auditoria de proveniência do código OpenJDK e dos scripts upstream, seguida de um teste de compilação controlado. Só depois disso deve ser criado um workflow de build e publicação de artefatos. Nenhum APK será gerado sem pedido explícito.
