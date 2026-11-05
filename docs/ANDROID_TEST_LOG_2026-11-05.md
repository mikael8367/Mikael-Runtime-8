# Diagnóstico do teste Android — 2026-11-05

## Resultado comprovado pelo latest.log

O teste no Samsung/Android 12 ARM64 confirma que a JRE iniciou e executou Minecraft 1.12.2 com Forge 14.23.5.2860, OptiFine HD U G5, LWJGL 2.9.4, GL4ES 1.1.5 e os mods ProjectE, Simple Storage Network e ProjectE Storage Bridge. O mundo singleplayer abriu, o servidor integrado iniciou e o encerramento salvou o mundo sem crash JVM visível.

Isto comprova inicialização e um teste funcional curto. Não comprova estabilidade prolongada, desempenho superior nem compatibilidade geral com modpacks.

## Problema 1 — JNA/Narrator e Android linker namespace

Trecho observado:

```
Couldn't load Narrator library
dlopen failed: ... JNA/temp/jna....tmp
is not accessible for the namespace "clns-4"
```

A biblioteca nativa temporária foi extraída em armazenamento compartilhado:
`/storage/emulated/0/CS LAUNCHER PLUS/.cache/JNA/temp/`.

O Android linker namespace bloqueou o carregamento desse caminho. O log não aponta falha da JVM: o aviso ocorreu depois de Forge/OptiFine carregarem e o jogo continuou até abrir o mundo.

### Correção aplicada no fork do launcher

Foi aplicado no repositório `mikael8367/CS-LAUNCHER-PLUS-fork`, em `JREUtils.getJavaArgs()`, o argumento:

```
-Djna.tmpdir=<Tools.DIR_CACHE>
```

`Tools.DIR_CACHE` vem de `Context.getCacheDir()`, portanto é o cache privado do aplicativo. O launcher já definia `java.io.tmpdir` e `jna.boot.library.path`; faltava definir explicitamente o diretório usado pelo JNA para extrair bibliotecas temporárias. Commit: [c5a544c](https://github.com/mikael8367/CS-LAUNCHER-PLUS-fork/commit/c5a544cf13c6f60a61ef55ddc65a652ea51ed1ad).

**Ainda precisa ser validado no aparelho:** compilar/instalar uma versão do launcher com esse commit e confirmar no próximo log que o JNA extrai em cache privado e que o aviso desapareceu. Não alterar permissões do linker namespace nem tentar carregar bibliotecas nativas de caminhos compartilhados.

Esta correção é no launcher/JNA; não exige mudar o binário HotSpot.

## Problema 2 — atrasos do servidor integrado

Trechos observados:

```
Running 2667ms behind, skipping 53 tick(s)
Running 3091ms behind, skipping 61 tick(s)
```

Os avisos ocorreram durante o primeiro carregamento/geração do mundo. Um log curto não permite atribuir a causa à JVM. Possíveis fatores incluem geração inicial de chunks, CPU/GPU, pressão de memória, GC, armazenamento e carga dos mods.

### Plano de medição

1. Repetir o teste no mesmo mundo já gerado, sem explorar chunks novos.
2. Registrar FPS, memória usada, memória máxima, duração das pausas e mensagens de GC.
3. Repetir com a mesma configuração e sem mods adicionais.
4. Comparar somente uma variável por execução (por exemplo, heap), mantendo render distance e demais opções iguais.
5. Não aplicar flags experimentais de GC ou aumentar heap às cegas: num aparelho com memória limitada isso pode piorar a pressão de RAM e causar encerramento pelo Android.

A render distance registrada caiu de 10 para 2; manter 2 durante a linha de base.

## Problema 3 — OpenGL/OptiFine

- `VboRegions not supported`: GL4ES reportou ausência de OpenGL 1.3/ARB_copy_buffer. É uma limitação do backend gráfico exposto, não uma falha Java.
- `Shaders can not be loaded, Fast Render is enabled`: shaders foram desativados pelo Fast Render. Para testar shaders, desativar Fast Render nas opções do OptiFine; no PowerVR/GL4ES não há garantia de compatibilidade ou bom desempenho.
- `OpenGL 2.1 gl4es wrapper 1.1.5`: confirma que o jogo está usando a camada GL4ES.

Não tentar corrigir capacidades OpenGL alterando a JVM; isso pertence ao launcher/backend gráfico.

## Problema 4 — ProjectE e receitas EMC

Os avisos `EMC Exploit` são emitidos pelo mapeador de EMC do ProjectE ao encontrar conversões cujo valor de saída supera o custo calculado. São dados/configuração de receitas do mod, não defeito da Runtime. Corrigir exige auditar receitas e valores EMC do modpack, sem alterar a JVM.

Os avisos `Can not get Fluid` indicam fluidos não registrados/encontrados no conjunto de mods carregado. Confirmar se os mods que registram esses fluidos estão instalados antes de alterar valores.

## Outros avisos não fatais

- `Skipping bad option: lastServer:`: opção inválida no arquivo de opções do Minecraft; limpar a entrada `lastServer`/regenerar apenas essa configuração se persistir.
- `Realms ... NullPointerException`: falha de verificação/autorização do Realms; não impediu o singleplayer.
- Forge informa alvo 14.23.5.2864 enquanto o teste executou 14.23.5.2860. Fazer uma execução separada com 2864 para validar a versão pretendida.

## Critérios para fechar a auditoria

- [ ] Repetir com `jna.tmpdir` privado e confirmar que o aviso JNA desapareceu.
- [ ] Testar Forge 14.23.5.2864 separadamente.
- [ ] Medir FPS/heap/GC em mundo já gerado e durante exploração.
- [ ] Fazer sessão de pelo menos 20–30 minutos sem crash, acompanhando memória.
- [ ] Auditar separadamente receitas EMC/fluidos do modpack.
- [ ] Guardar o novo `latest.log` completo e, se houver crash, o crash report.

## Limite da correção

A Runtime não deve mascarar avisos que pertencem ao launcher, ao GL4ES ou aos mods. A primeira ação corretiva para JNA é configurar o diretório temporário no launcher; os avisos de desempenho precisam de medição reproduzível antes de mudar flags ou código da JVM.
