# Mikael Runtime 8

Distribuição experimental de runtime Java 8 para Android ARM64, com foco em compatibilidade com Minecraft Java 1.12.2 Forge e integração com FCL.

## Estado atual

Este repositório está na fase de estruturação. Ainda não contém uma JVM compilada nem uma runtime instalável.

## Objetivos

- Base OpenJDK 8 validada para Android ARM64.
- Compatibilidade com Minecraft 1.12.2, Forge e bibliotecas JNI necessárias.
- Perfil de execução voltado a estabilidade e desempenho mensurável.
- Integração documentada com FCL e, futuramente, um aplicativo próprio.
- Testes de inicialização, memória, coleta de lixo, compatibilidade e estabilidade.

## Princípios

1. Não declarar ganhos de FPS sem benchmarks reproduzíveis.
2. Não distribuir binários até validar origem, arquitetura e licenças.
3. Priorizar compatibilidade e estabilidade antes de otimizações agressivas.
4. Não incluir APK neste projeto enquanto não houver pedido explícito.

## Planejamento

Consulte `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/BASE_SELECTION.md` e `docs/TESTING.md`.

## Licenças

O código original deste repositório será licenciado conforme `LICENSE`. Componentes OpenJDK e dependências mantêm suas respectivas licenças e avisos, que deverão acompanhar qualquer distribuição.
