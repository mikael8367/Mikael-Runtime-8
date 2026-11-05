# Mikael Runtime 8

Projeto experimental de uma distribuição Java 8 para Android ARM64, com foco em Minecraft Java 1.12.2 Forge e integração planejada com FCL e CS Launcher Plus.

## Estado atual

**Ainda não existe JVM compilada, JRE instalável ou runtime pronta para selecionar no launcher.** O projeto possui perfil experimental, validadores, testes, auditorias de fonte/patches e kits de diagnóstico. Esses componentes não substituem uma JVM.

## O que já existe

- Perfil experimental Java 8 / AArch64 para Minecraft 1.12.2.
- Validadores de perfil e contrato de compatibilidade.
- Testes automatizados de regressão e empacotamento.
- Pré-verificação dos patches Android sobre OpenJDK 8u.
- Auditoria da receita histórica Pojav e auditoria da receita atual MojoLauncher.
- Validador/empacotador MultiRT para CS Launcher Plus.
- Kit de diagnóstico Java 8 para testar uma runtime que já exista.

## Base de compilação investigada

Foi localizado o fork ativo [MojoLauncher/android-openjdk-build-multiarch](https://github.com/MojoLauncher/android-openjdk-build-multiarch), com workflow de build para AArch64 e publicação de JRE 8 de referência. A receita ainda tem riscos que precisam ser corrigidos antes de executá-la neste projeto. Consulte [docs/MOJO_OPENJDK8_RECIPE_REVIEW.md](docs/MOJO_OPENJDK8_RECIPE_REVIEW.md).

## Validar pelo celular

- [Actions do projeto](https://github.com/mikael8367/Mikael-Runtime-8/actions)
- Workflow **Audit maintained OpenJDK 8 ARM64 recipe**: confere a identidade da receita e gera relatório de riscos; não compila JVM.
- Workflow **OpenJDK 8 ARM64 source preflight**: verifica a fonte OpenJDK e aplicação sequencial dos patches; não compila JVM.
- Workflow **Build Android Runtime Test Kit**: gera apenas o JAR de diagnóstico; não contém JVM.

## Critérios para chamar de runtime válida

1. Compilar HotSpot Server AArch64 e bibliotecas Java para Android/Bionic.
2. Fixar fonte, toolchain e dependências com hashes verificados.
3. Aplicar todos os patches sem rejeições ou aplicação parcial.
4. Validar ELF64/AArch64, ABI, símbolos e dependências dinâmicas.
5. Empacotar JRE no formato aceito pelo launcher, com manifesto e SHA-256.
6. Executar `java -version`, JNI, threads, GC e smoke tests no Android real.
7. Testar FCL/CS Launcher Plus e Minecraft 1.12.2 com Forge, OptiFine e modpack.

A compatibilidade com mods e OptiFine só será declarada depois desses testes. A JVM não substitui LWJGL, GL4ES, assets, classpath ou o loader do launcher.

## Objetivos

- Android `arm64-v8a` / AArch64.
- Java 8 para Minecraft 1.12.2.
- Compatibilidade progressiva com Forge, OptiFine, mods e modpacks.
- Integração com FCL e CS Launcher Plus.
- Prioridade em estabilidade; otimizações de FPS somente após benchmark reproduzível.

Nenhum APK será gerado sem pedido explícito.

## Licenças

O código original deste repositório usa a licença indicada em LICENSE. OpenJDK e dependências mantêm suas próprias licenças e avisos; a licença MIT deste repositório não altera essas obrigações.
