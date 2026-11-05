# Mikael Runtime 8

Distribuição experimental Java 8 para Android ARM64/AArch64, direcionada ao Minecraft Java 1.12.2, com foco em estabilidade e integração com CS Launcher Plus/FCL.

## Estado atual

**A JRE foi compilada, empacotada e executada no Android 12 ARM64.** O primeiro teste real iniciou Minecraft 1.12.2 com Forge 14.23.5.2860, OptiFine HD U G5, LWJGL 2.9.4/GL4ES 1.1.5 e os mods ProjectE, Simple Storage Network e ProjectE Storage Bridge. O mundo singleplayer abriu e foi salvo no encerramento.

Isso comprova o teste funcional inicial, não compatibilidade universal, estabilidade prolongada ou ganho de FPS. O teste ainda não confirma Forge 14.23.5.2864.

## O que existe

- OpenJDK 8 HotSpot Server compilado para Android ARM64.
- Pipeline reprodutível com fontes, patches e dependências fixados.
- Validação ELF64/AArch64 e empacotamento MultiRT `.tar.xz` para CS Launcher Plus.
- Manifesto e SHA-256 do artefato.
- Testes automatizados para preparação e empacotamento.
- Relatório do primeiro teste no aparelho: [Diagnóstico Android 2026-11-05](docs/ANDROID_TEST_LOG_2026-11-05.md).

## Build e artefato

Workflow: [Build Mikael Runtime 8 ARM64](.github/workflows/build-mikael-runtime8-arm64.yml).

O artefato `Mikael-Runtime-8-Android-ARM64` contém a runtime `.tar.xz`, checksum e relatórios de build. Consulte a execução do workflow e baixe o artefato correspondente à compilação validada.

## Resultado do primeiro teste

- JVM Java 8 ARM64: iniciou.
- Android 12 / CS Launcher Plus: iniciou.
- Forge 14.23.5.2860: carregou.
- OptiFine HD U G5: carregou.
- ProjectE, Simple Storage Network e ProjectE Storage Bridge: carregaram.
- Mundo singleplayer: abriu, iniciou servidor integrado e salvou.
- Narrator/JNA: aviso não fatal; a extração nativa ocorreu em armazenamento compartilhado e o Android bloqueou o carregamento pelo linker namespace.
- Servidor integrado: avisos de atraso de 2,6–3,1 segundos durante o teste curto; causa ainda não isolada.

Os detalhes e o plano de validação estão em [docs/ANDROID_TEST_LOG_2026-11-05.md](docs/ANDROID_TEST_LOG_2026-11-05.md).

## Limites técnicos

A JVM não substitui nem controla diretamente o launcher, JNA, LWJGL, GL4ES, driver gráfico, mods ou configurações de receitas. Avisos do OpenGL/GL4ES e do ProjectE precisam ser corrigidos na camada correspondente. Não serão adicionadas flags experimentais de GC ou de heap sem medições reproduzíveis.

## Próximas validações

1. Configurar JNA para extrair bibliotecas nativas em diretório privado do app e confirmar novo log.
2. Testar Forge 14.23.5.2864.
3. Medir FPS, memória e pausas de GC em mundo já gerado e durante exploração.
4. Fazer sessão prolongada sem crash.
5. Auditar receitas EMC/fluidos do modpack separadamente.

Nenhum APK será gerado sem pedido explícito.

## Licenças

O código original deste repositório usa a licença indicada em LICENSE. OpenJDK e dependências mantêm suas próprias licenças e avisos.
