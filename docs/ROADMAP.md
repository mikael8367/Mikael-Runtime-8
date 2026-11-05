# Roadmap

## Marco 0 — Estrutura do projeto
- [x] Criar documentação inicial.
- [x] Definir escopo e critérios de qualidade.
- [ ] Registrar a distribuição OpenJDK 8 escolhida e sua licença.
- [ ] Confirmar viabilidade técnica do alvo Android ARM64.

## Marco 1 — Protótipo Java 8 ARM64
- [ ] Preparar ambiente de compilação reproduzível.
- [ ] Compilar uma runtime mínima a partir de fonte validada.
- [ ] Verificar ABI, dependências nativas e nível mínimo do Android.
- [ ] Executar testes básicos de JVM no Android real.

## Marco 2 — Compatibilidade Minecraft
- [ ] Testar Minecraft 1.12.2 sem mods.
- [ ] Testar Forge 14.23.5.2864.
- [ ] Testar carregamento de mods em grupos pequenos.
- [ ] Testar OptiFine separadamente.
- [ ] Investigar JNI e renderização no launcher/driver usados.

## Marco 3 — Desempenho e estabilidade
- [ ] Criar benchmark repetível.
- [ ] Comparar runtime-base e versão modificada no mesmo aparelho.
- [ ] Medir FPS médio e mínimos, RAM, tempo de inicialização e pausas de GC.
- [ ] Reverter otimizações que reduzam compatibilidade ou estabilidade.

## Marco 4 — Integração
- [ ] Documentar instalação e seleção no FCL.
- [ ] Criar testes de configuração e diagnóstico.
- [ ] Planejar aplicativo próprio com abas inferiores animadas.
- [ ] Preparar pacote distribuível somente após auditoria de licenças e testes.

## Critérios para considerar uma versão pronta
- Inicializa repetidamente no Android ARM64 alvo.
- Passa testes básicos de Java e Minecraft definidos em docs/TESTING.md.
- Não apresenta regressões críticas conhecidas.
- Tem origem, versão, licenças e dependências documentadas.
- Benchmarks incluem ambiente, configurações e resultados brutos.
- Não anuncia ganho de FPS sem comparação válida.
