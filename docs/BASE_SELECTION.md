# Seleção da base Java 8 para Android

## Candidato prioritário atual

Foi localizado o fork ativo [MojoLauncher/android-openjdk-build-multiarch](https://github.com/MojoLauncher/android-openjdk-build-multiarch), atualizado em 2026-10-22. A revisão desta data usa o commit imutável observado:

`a0d811b6c5ebd251374751438ec8b635f0746ab4`

O fork mantém workflow para compilar OpenJDK 8 para AArch64 e publicar um JRE de referência usado pelo ecossistema Pojav/Mojo. Isso é uma rota concreta para reproduzir a compilação, mas não prova por si só que o pacote seja compatível com CS Launcher Plus ou com o aparelho do usuário.

## Riscos ainda presentes

A receita atual ainda:
- tolera falhas na aplicação de patches com `git apply --reject` e `|| echo`;
- clona OpenJDK sem fixar commit;
- baixa FreeType/CUPS e NDK sem checksum verificado;
- extrai o NDK imediatamente após download;
- baixa `termux-elf-cleaner` por tag, não commit;
- inicia tmate em falha do workflow;
- depende de NDK r10e/API 21, uma toolchain histórica.

A auditoria automatizada está em [MOJO_OPENJDK8_RECIPE_REVIEW.md](MOJO_OPENJDK8_RECIPE_REVIEW.md). A auditoria não executa os scripts upstream.

## Candidato histórico

O repositório original [PojavLauncherTeam/android-openjdk-build-multiarch](https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch) está arquivado. Seu commit e seus patches continuam documentados em [OPENJDK8_ARM64_BUILD.md](OPENJDK8_ARM64_BUILD.md), mas o fork Mojo é a referência mais atual para reproduzir o build.

## ABI e integração

O alvo é Android `arm64-v8a` (AArch64). Binários Linux AArch64 genéricos não são automaticamente compatíveis com Android/Bionic. Além da JVM, o launcher continua responsável por JNI do ambiente, LWJGL, GL4ES, assets, classpath e loader de mods.

## Decisão

Usar a receita Mojo como base de investigação/reprodução, mas não executar o build completo até que os passos inseguros sejam substituídos por etapas fixadas, verificadas e com falha fatal. Nenhum binário de terceiros será rebatizado como Mikael Runtime 8.
