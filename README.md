# Mikael Runtime 8

Projeto experimental de uma distribuição Java 8 para Android ARM64, com foco em Minecraft Java 1.12.2 Forge e integração planejada com FCL e um aplicativo próprio.

## Estado atual

O projeto já possui documentação técnica, um perfil experimental para Minecraft 1.12.2, um validador Python, testes de regressão e GitHub Actions. **Ainda não possui JVM compilada, JRE instalável ou runtime pronta para selecionar no FCL.**

## O que já existe

- config/minecraft-1.12.2.json: perfil experimental Java 8 / AArch64.
- scripts/validate_profile.py: valida versão, arquitetura, heap e argumentos JVM.
- tests/test_profile.py: testes de regressão do validador.
- .github/workflows/validate.yml: validação automática do projeto.
- docs/: arquitetura, seleção da base, formato do perfil, testes e roadmap.

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

O perfil JSON não é uma JVM. Uma VM iniciar também não prova que Forge, OptiFine, JNI ou renderização funcionarão. A base OpenJDK e a toolchain Android ainda precisam ser selecionadas, auditadas e compiladas.

Consulte docs/ROADMAP.md para o estado das etapas e docs/BUILD_STATUS.md para o bloqueio atual de compilação.

## Licenças

O código original deste repositório usa a licença indicada em LICENSE. OpenJDK e dependências mantêm suas próprias licenças e avisos; a licença MIT deste repositório não altera essas obrigações.
