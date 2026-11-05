# Mikael Runtime 8

Projeto experimental de uma distribuição Java 8 para Android ARM64, com foco em Minecraft Java 1.12.2 Forge e integração planejada com FCL e um aplicativo próprio.

## Estado atual

O projeto já possui documentação técnica, um perfil experimental para Minecraft 1.12.2, um validador Python, testes de regressão e GitHub Actions. **Ainda não possui JVM compilada, JRE instalável ou runtime pronta para selecionar no FCL.**

## O que já existe

- config/minecraft-1.12.2.json: perfil experimental Java 8 / AArch64.
- scripts/validate_profile.py: valida versão, arquitetura, heap e argumentos JVM.
- tests/test_profile.py: testes de regressão do validador.
- .github/workflows/validate.yml: validação automática do projeto.
- config/compatibility-minecraft-1.12.2.json: contrato verificável de compatibilidade para Forge, OptiFine, mods e modpacks.
- scripts/validate_compatibility.py e tests/test_compatibility.py: validador e testes para esse contrato.
- docs/MOD_COMPATIBILITY.md: requisitos do classpath, JNI, LWJGL, OptiFine e testes por etapas.
- docs/: arquitetura, seleção da base, formato do perfil, testes, roadmap e compatibilidade com CS Launcher Plus.
- scripts/package_cslauncher_runtime.py: valida e empacota uma JRE Java 8 ARM64 no formato MultiRT do CS Launcher Plus.
- tests/device-smoke/: teste Java 8 para verificar uma runtime no próprio Android.
- .github/workflows/build-test-kit.yml: compila e publica um kit de diagnóstico para baixar pelo celular.

## Validar

Em um ambiente com Python 3.12 ou compatível:

    python scripts/validate_profile.py
    python -m unittest discover -s tests -v

O GitHub Actions executa essas verificações em alterações na branch main.

## Objetivos técnicos

- Java 8 para Android arm64-v8a.
- Compatibilidade progressiva com Minecraft 1.12.2 e Forge.
- Integração com FCL e, posteriormente, aplicativo próprio.
- Prioridade em estabilidade; otimizações de FPS somente após benchmark reproduzível.

## Limitações importantes

O kit de diagnóstico também não é uma JVM: ele serve para testar uma runtime Java 8 que já esteja instalada. A Mikael Runtime 8 ainda não possui binário próprio para selecionar no launcher. O perfil e o contrato de compatibilidade não são uma JVM. O projeto define Forge 14.23.5.2864 e OptiFine HD U G5 como alvos de teste, mas ainda não executou esses componentes com uma runtime própria. A VM, JNI, classpath, bibliotecas LWJGL e renderização precisam ser validados em Android real. A base OpenJDK e a toolchain Android ainda precisam ser selecionadas, auditadas e compiladas.

Para testar uma runtime existente no celular, siga [tests/device-smoke/ANDROID_TEST_GUIDE.md](tests/device-smoke/ANDROID_TEST_GUIDE.md) e baixe o artefato do workflow **Build Android Runtime Test Kit** em Actions.

Consulte [docs/ROADMAP.md](docs/ROADMAP.md), [docs/BUILD_STATUS.md](docs/BUILD_STATUS.md), [docs/OPENJDK8_SOURCE_AUDIT.md](docs/OPENJDK8_SOURCE_AUDIT.md) e [docs/OPENJDK8_ANDROID_PATCH_REVIEW.md](docs/OPENJDK8_ANDROID_PATCH_REVIEW.md), [docs/OPENJDK8_PATCH_FINDINGS.md](docs/OPENJDK8_PATCH_FINDINGS.md) e [docs/OPENJDK8_PATCH_INVENTORY.md](docs/OPENJDK8_PATCH_INVENTORY.md) e [docs/OPENJDK8_TEST_MATRIX.md](docs/OPENJDK8_TEST_MATRIX.md), [docs/MOD_COMPATIBILITY.md](docs/MOD_COMPATIBILITY.md) e [config/compatibility-minecraft-1.12.2.json](config/compatibility-minecraft-1.12.2.json) para auditorias, compatibilidade e estado das etapas.

## Licenças

O código original deste repositório usa a licença indicada em LICENSE. OpenJDK e dependências mantêm suas próprias licenças e avisos; a licença MIT deste repositório não altera essas obrigações.
