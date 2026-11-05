# Revisão dos patches Android do OpenJDK 8

**Data:** 2026-11-05  
**Upstream auditado:** `PojavLauncherTeam/android-openjdk-build-multiarch`, branch `buildjre8`, commit `04b90441da7e9649cb6508a037423f08d1fc531f`.  
**Escopo efetivamente lido:** diff completo `jdk8u_android.diff` recuperado pelo blob SHA, mais os patches pequenos `jdk8u_android_main.diff`, `jdk8u_android_aarch32.diff` e `jdk8u_android_page_trap_fix.diff`. O inventário de 207 caminhos está em [OPENJDK8_PATCH_INVENTORY.md](OPENJDK8_PATCH_INVENTORY.md).

## Estado da auditoria por subsistema

| Subsistema | Estado | Evidência/pendência |
|---|---|---|
| HotSpot / OS Linux | Revisão parcial | Três patches pequenos alteram chamadas Linux/Bionic e sincronização |
| Sinais / page trap | Revisão parcial | Patch altera aquisição de lock no caminho de page trap |
| AArch32 | Revisão parcial | Patch condicional remove include de FPU |
| AArch64 | Não auditado em profundidade | Patch principal não pôde ser lido integralmente |
| JNI | Não auditado | Requer leitura do patch principal e testes JNI |
| GC / gerenciamento de memória | Não auditado | Requer rastrear alterações HotSpot e testes de stress |
| JIT / compilador | Não auditado | Requer revisão de mudanças por arquitetura e validação de código gerado |
| Java2D / AWT / fontes | Não auditado | Requer revisão do patch principal e execução gráfica real |
| Threads / sincronização | Parcial | Page trap patch examinado; restante não auditado |
| Bionic / libc / syscalls | Parcial | Mudanças em includes/syscalls e símbolos Linux examinadas |

## Achados nos patches pequenos

### [MÉDIO] Desativação de `dlvsym` no Android

**Arquivo:** `patches/jdk8u_android_main.diff`  
**Mudança:** em Android, a resolução versionada `dlvsym(..., "libnuma_1.1")` é substituída por ponteiro nulo, e o código tenta o fallback com `dlsym`.

**Impacto:** evita depender de API de versionamento de símbolos que não é fornecida da mesma forma pelo Bionic. É uma adaptação plausível, mas precisa ser testada com todas as bibliotecas carregadas pela JVM e não prova compatibilidade geral de JNI.

**Teste necessário:** inicialização da VM e carregamento de bibliotecas JNI nativas no Android alvo.

### [BAIXO/MÉDIO] `os::loadavg` retorna -1 no Android

**Arquivo:** `patches/jdk8u_android_main.diff`  
**Mudança:** a função deixa de chamar `getloadavg` e retorna `-1` no Android.

**Impacto:** consumidores dessa API recebem indisponibilidade de load average. Não deve ser confundido com erro de CPU ou falha de GC. Validar se ferramentas de monitoramento ou código da JVM dependem de um valor válido.

### [MÉDIO] Includes de syscall específicos do Android

**Arquivos:** `jdk8u_android_main.diff` e `jdk8u_android_aarch32.diff`  
**Mudança:** troca de `syscall.h` por `sys/syscall.h` no Android e exclusão de `gnu/libc-version.h`.

**Impacto:** adapta o código às headers Bionic em vez de glibc. A compilação precisa confirmar que os símbolos e estruturas usados continuam definidos para a API mínima escolhida.

### [MÉDIO] Patch de page trap muda caminho de sincronização

**Arquivo:** `patches/jdk8u_android_page_trap_fix.diff`  
**Mudança:** substitui `Thread::muxAcquire` por uma obtenção de `ParkEvent` condicional à inicialização de TLS e chamada `Thread::muxAcquireW`.

**Impacto:** toca sincronização em caminho sensível de HotSpot. Um erro pode causar deadlock, corrida ou comportamento incorreto durante inicialização/sinais. Não há evidência suficiente para aprovar a alteração apenas pela leitura do diff.

**Testes obrigatórios:** inicialização repetida da JVM, stress multithread, alocação/GC sob pressão, shutdown e cenários de sinal/page trap no dispositivo real. Comparar com build sem o patch quando possível.

### [BAIXO/MÉDIO] Include de controle FPU removido para AArch32 Android

**Arquivo:** `patches/jdk8u_android_aarch32.diff`  
**Mudança:** protege `fpu_control.h` com `#ifndef __ANDROID__`.

**Impacto:** evita header ausente no Bionic. Não é evidência de que a configuração de ponto flutuante e as opções de compilação estejam corretas para toda CPU ARM32.

## Patch principal: revisão estática realizada

O patch `jdk8u_android.diff` foi recuperado integralmente por SHA e teve seus caminhos e principais alterações examinados. Os achados estão registrados em [OPENJDK8_PATCH_FINDINGS.md](OPENJDK8_PATCH_FINDINGS.md). A revisão continua estática: não houve compilação nem execução no Android.

SHA upstream informado pela árvore Git: `801ec26807256e5206616c2da14c80676519bce9`.

Ainda é necessário aprofundar os subsistemas que dependem de execução e testes (JNI, GC, JIT, threads, AWT, rede e memória). Não considerar o patch aprovado apenas por leitura.

## Critérios de aprovação antes de compilar

- [x] Recuperar e inventariar 100% dos caminhos de `jdk8u_android.diff`.
- [ ] Mapear cada arquivo alterado para seu subsistema.
- [ ] Confirmar compatibilidade dos patches com SHA fixo do OpenJDK 8u.
- [ ] Aplicar patches sem ignorar falhas; patch parcialmente aplicado deve abortar o build.
- [ ] Validar ABI AArch64 e dependências ELF contra a API Android escolhida.
- [ ] Testar JNI, GC, JIT, threads, sinais, Java2D e inicialização no Android 12 ARM64.
- [ ] Comparar estabilidade e desempenho com baseline, sem presumir ganho de FPS.
- [ ] Registrar logs, hashes, toolchain e artefatos de teste.

## Referências

- [Patch Android principal](https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/blob/buildjre8/patches/jdk8u_android.diff)
- [Patch Android AArch64/Linux principal pequeno](https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/blob/buildjre8/patches/jdk8u_android_main.diff)
- [Patch AArch32](https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/blob/buildjre8/patches/jdk8u_android_aarch32.diff)
- [Patch page trap](https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/blob/buildjre8/patches/jdk8u_android_page_trap_fix.diff)

## Correção do processo de aplicação (2026-11-05)

A auditoria do workflow encontrou dois defeitos no próprio preflight, que poderiam produzir um diagnóstico falso:

1. O workflow verificava o segundo patch contra a árvore OpenJDK ainda sem o primeiro patch. Patches sequenciais podem depender do estado produzido pelo patch anterior; a validação foi alterada para aplicar o patch principal primeiro e só então verificar/aplicar `jdk8u_android_main.diff`.
2. A verificação e a aplicação usavam políticas de whitespace diferentes. Agora ambas usam `--whitespace=fix`, e `git diff --check` é executado depois de cada aplicação.

Também foram adicionadas verificações dos Git blob SHAs dos dois patches, para impedir que conteúdo diferente seja usado sob os mesmos nomes.

**Importante:** isso corrige o mecanismo de validação/aplicação, não prova que todos os hunks do patch principal são corretos. A execução do preflight e a compilação real continuam necessárias. O patch AArch32 não deve ser aplicado ao alvo AArch64; o patch page-trap permanece separado e não foi integrado automaticamente, pois altera sincronização sensível do HotSpot.
