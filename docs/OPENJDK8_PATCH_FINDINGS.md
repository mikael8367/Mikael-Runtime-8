# Achados complementares — patch Android OpenJDK 8

**Origem:** PojavLauncherTeam/android-openjdk-build-multiarch, branch `buildjre8`.
**Patch SHA:** `801ec26807256e5206616c2da14c80676519bce9`.
**Inventário:** [OPENJDK8_PATCH_INVENTORY.md](OPENJDK8_PATCH_INVENTORY.md).

## Resultado

O patch principal foi recuperado integralmente e seu diff contém 207 caminhos, 58.398 linhas adicionadas e 114 removidas. A revisão é estática; não houve build nem execução no Android. O patch não está aprovado para integração direta.

## Achados prioritários

1. **tinyiconv — tratamento de UTF-8 inválido:** a implementação usa o retorno de conversão multibyte como contador de bytes consumidos. Os caminhos de substituição/ignorar precisam separar erro de conversão e comprimento real da sequência, para evitar avanço incorreto do cursor.
2. **tinyiconv — caractere NUL:** o retorno zero da conversão UTF-8 não é tratado como consumo de um byte. É necessário teste específico para U+0000 para evitar ausência de progresso no laço.
3. **AWT/GLX:** o build remove partes do backend X11/GLX, mas uma função de detecção reporta GLX disponível no Android. Definir modo headless ou implementar backend Android consistente.
4. **Localização de bibliotecas nativas:** os helpers que consultam `/proc/self/maps` precisam validar o formato da linha, os ponteiros encontrados e a capacidade do buffer de destino.
5. **getifaddrs/Netlink:** validar tamanho de cada atributo, família de endereço, prefixo de rede e limpeza de estruturas em falhas parciais.
6. **glibc_bionic.c:** há um provável erro de identificador no caso que retorna a versão da libc. Confirmar se o arquivo é realmente incluído no build antes de classificar como bloqueio de compilação.
7. **Locale/iconv:** a implementação fornece um conjunto reduzido de encodings e formatos de locale. Testar pt-BR, UTF-8, UTF-16, UTF-32, caracteres nulos e entradas inválidas.
8. **AArch64:** a alteração de instrução de prefetch precisa ser verificada com o assembler escolhido e submetida a testes de cópia de memória no dispositivo.

## Situação por subsistema

| Área | Situação |
|---|---|
| HotSpot / OS Linux | Diff examinado; requer testes de inicialização, procfs, sinais, perf e rede |
| AArch64 / ABI | Mudanças identificadas; build e validação no ARM64 pendentes |
| JNI / bibliotecas nativas | Arquivos identificados; testes de carga, unload, threads e ABI pendentes |
| GC / memória | Não há evidência de otimização validada; stress de heap e pausas pendentes |
| JIT | Correção de código gerado e benchmark pendentes |
| AWT / Java2D / fontes | Backend alterado; modo headless e fontes precisam de teste |
| Threads / sincronização | Testes de concorrência e shutdown pendentes |
| Rede | Implementação Netlink requer testes IPv4/IPv6 e interfaces variadas |
| Locale / iconv | Compatibilidade parcial; testes de conversão e locale pendentes |

## Critérios antes de integração

- [ ] Corrigir e testar conversão UTF-8 inválida e U+0000.
- [ ] Resolver o contrato AWT/GLX.
- [ ] Validar buffers e ponteiros nos helpers de caminho de bibliotecas.
- [ ] Fortalecer parser Netlink e limpeza em erro.
- [ ] Confirmar inclusão de glibc_bionic.c no build.
- [ ] Auditar licenças e proveniência dos headers ICU/Unicode importados.
- [ ] Fixar a revisão do OpenJDK 8u e aplicar patches sem rejeições.
- [ ] Compilar isoladamente e testar JNI, GC, JIT, threads, rede e AWT em Android ARM64.
- [ ] Medir desempenho no mesmo dispositivo e nas mesmas condições.

**Conclusão:** manter o patch como referência de portabilidade, não como base pronta. Não gerar runtime distribuível antes de corrigir e validar os itens acima.
