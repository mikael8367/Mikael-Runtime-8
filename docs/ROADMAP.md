# Roadmap

## Marco 0 — Estrutura e validação do projeto
- [x] Criar documentação inicial e definir o escopo.
- [x] Documentar o candidato OpenJDK 8 Android ARM64 e suas limitações.
- [x] Criar validador do perfil Minecraft 1.12.2.
- [x] Criar testes de regressão para regras do perfil.
- [x] Executar validações de perfil automaticamente no GitHub Actions.
- [x] Documentar o contrato MultiRT do CS Launcher Plus.
- [x] Criar empacotador e testes do arquivo de runtime compatível com CS Launcher Plus.
- [ ] Confirmar os testes no GitHub Actions.
- [ ] Confirmar execução verde do workflow no GitHub.

## Marco 1 — Escolha e reprodução da base Java 8
- [ ] Fixar a origem e o commit exato do código-fonte escolhido.
- [x] Fazer auditoria estática inicial dos scripts de build, patches e workflow upstream.
- [x] Fazer revisão parcial dos três patches Android pequenos acessíveis.
- [ ] Recuperar e revisar integralmente o patch Android principal (2,38 MB).
- [ ] Auditar JNI, GC, JIT, Java2D, threads, sinais e memória com testes específicos.
- [ ] Auditar licença, avisos e dependências de cada componente e gerar inventário/SBOM.
- [ ] Resolver uma toolchain de compilação reproduzível para Android ARM64.
- [ ] Reproduzir a compilação em ambiente isolado; não assumir que a receita antiga funciona.
- [ ] Registrar hashes e proveniência dos artefatos gerados.

## Marco 2 — Protótipo Java 8 ARM64
- [ ] Compilar uma runtime mínima a partir de fonte validada.
- [ ] Verificar ABI, dependências nativas e nível mínimo do Android.
- [ ] Executar java -version e testes básicos de classes, threads e JNI em Android real.
- [ ] Validar carregamento e permissões de arquivos no Android 12.

## Marco 3 — Compatibilidade Minecraft
- [ ] Testar Minecraft 1.12.2 sem mods.
- [ ] Testar Forge 14.23.5.2864.
- [ ] Adicionar mods em grupos pequenos e manter logs.
- [ ] Testar OptiFine separadamente.
- [ ] Validar renderização, LWJGL/JNI e integração com o FCL.

## Marco 4 — Desempenho e estabilidade
- [ ] Criar benchmark repetível no mesmo aparelho.
- [ ] Comparar runtime-base e candidata sob condições idênticas.
- [ ] Medir FPS médio e 1% low, RAM, inicialização e pausas de GC.
- [ ] Reverter otimizações que causem regressões de compatibilidade ou estabilidade.

## Marco 5 — Integração e distribuição
- [ ] Documentar instalação e seleção no FCL.
- [ ] Implementar integração com aplicativo próprio, com abas inferiores animadas.
- [ ] Auditar licenças, dependências e arquivos incluídos no pacote.
- [ ] Preparar distribuição somente após testes em dispositivo real.

## Critérios para considerar uma versão pronta
- Inicializa repetidamente no Android ARM64 de destino.
- Passa testes Java e Minecraft definidos em docs/TESTING.md.
- Não apresenta regressões críticas conhecidas.
- Tem origem, versão, licenças e dependências documentadas.
- Benchmarks incluem ambiente, configurações e resultados brutos.
- Não anuncia ganho de FPS sem comparação válida.
