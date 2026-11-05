# Revisão da base OpenJDK 8 Android mantida pelo MojoLauncher

## Resultado da investigação

Em 2026-11-05 foi localizado um fork ativo da receita histórica: [MojoLauncher/android-openjdk-build-multiarch](https://github.com/MojoLauncher/android-openjdk-build-multiarch). O repositório não está arquivado e a branch `buildjre8` recebeu atualização em 2026-10-22.

Revisão usada nesta auditoria:
- Repositório: `MojoLauncher/android-openjdk-build-multiarch`
- Branch observada: `buildjre8`
- Commit observado: `a0d811b6c5ebd251374751438ec8b635f0746ab4`
- Workflow: `.github/workflows/build.yml`
- Arquitetura alvo: `aarch64`
- Runner upstream: Ubuntu 22.04
- NDK documentado pelo projeto: r10e, API mínima 21
- Variante configurada para AArch64: HotSpot server

O workflow upstream compila quatro arquiteturas e empacota o JRE. O PojavLauncher da branch `v3_openjdk` aponta para os pacotes publicados pelo MojoLauncher, inclusive o JRE 8. Isso demonstra que existe uma rota real de compilação e distribuição usada pelo ecossistema, diferente do kit de diagnóstico deste repositório.

## Artefato público observado (referência, não Mikael Runtime)

A release `rolling` observada contém `jre8-pojav.zip`, com digest publicado pelo GitHub:

`sha256:a97cf40dc2eb1e642c3b5188260d7c42908a8f603556cc52492bf29d03eab6b3`

Esse pacote é de terceiros, usa convenções Pojav/Mojo e não foi copiado nem rebatizado como Mikael Runtime 8. A tag `rolling` é mutável. O digest acima identifica apenas o arquivo observado nesta revisão; não deve ser tratado como um pin permanente da release.

## Bloqueios encontrados na receita atual

A atualização do fork não removeu automaticamente os riscos de segurança/reprodutibilidade encontrados na receita:

1. `buildjdk.sh` ainda usa `git apply --reject` e tolera falhas com `|| echo`; isso pode deixar uma árvore parcialmente patchada.
2. `clonejdk.sh` ainda clona `openjdk/jdk8u` sem fixar um commit.
3. `getlibs.sh` baixa FreeType e CUPS sem validar SHA-256 ou assinatura.
4. `setdevkitpath.sh` seleciona NDK r10e, mas o workflow/`ci_build_global.sh` não mostra uma etapa explícita que forneça esse NDK ao diretório esperado; isso é um bloqueio de reprodução.
5. `maketoolchain.sh` baixa o GCC toolchain pré-compilado sem checksum; `tarjdk.sh` clona `termux-elf-cleaner` por tag, sem fixar o commit.
6. O workflow ainda inicia uma sessão tmate quando o job falha.
7. O NDK r10e e a API 21 são uma toolchain histórica; a compilação deve ser reproduzida e os ELF resultantes precisam ser auditados para Android/Bionic.

A pré-verificação deste repositório aplica os dois patches Android principais com `git apply --check` e falha em qualquer rejeição. Isso reduz um risco, mas não torna segura a execução direta da receita upstream.

## Decisão técnica

A base Mojo é agora o candidato prioritário para reproduzir o build ARM64, em vez de tratar apenas o fork Pojav arquivado como referência. Ainda não está liberado executar o pipeline completo até substituir ou neutralizar os passos inseguros acima.

Próximos critérios:
- [ ] Fixar e auditar todos os commits e blobs usados.
- [ ] Fazer clone do OpenJDK por SHA imutável.
- [ ] Verificar os downloads por SHA-256 oficial antes de extrair.
- [ ] Aplicar patches com `git apply --check` e falha fatal, sem `--reject`.
- [ ] Remover tmate e qualquer execução interativa do CI.
- [ ] Compilar HotSpot AArch64 e bibliotecas.
- [ ] Verificar ELF64/AArch64, dependências dinâmicas, símbolos Bionic e API mínima.
- [ ] Executar `java -version` e smoke tests no Android real.
- [ ] Testar FCL/CS Launcher Plus e Minecraft 1.12.2 com Forge/OptiFine/modpack.

## Conclusão

A existência de uma receita ativa e de um JRE 8 público de referência é um avanço técnico importante. **A Mikael Runtime 8 ainda não foi compilada.** Não usar o pacote de terceiros como se fosse um build próprio. A primeira entrega válida precisa vir de um build rastreável deste projeto e passar pela validação no dispositivo.
