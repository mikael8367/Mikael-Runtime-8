# Auditoria do código-fonte OpenJDK 8 para Android ARM64

**Data da revisão:** 2026-11-05  
**Escopo:** revisão estática do pipeline público PojavLauncherTeam/android-openjdk-build-multiarch, branch `buildjre8`, commit `04b90441da7e9649cb6508a037423f08d1fc531f`, e dos pontos de entrada do OpenJDK 8 usados por ele.  
**Resultado:** candidato tecnicamente relevante, mas não aprovado para execução/compilação automática nem para virar a base de produção da Mikael Runtime 8.

 > Esta é uma auditoria estática do wrapper e do diff Android identificado. Não equivale à auditoria de todo o código-base OpenJDK não modificado, nem a uma compilação reproduzível ou validação no Android.

## Resumo executivo

O projeto Pojav é uma receita histórica para portar OpenJDK 8 a Android, inclusive AArch64. Ele não deve ser tratado como uma distribuição pronta nem como uma base segura para executar diretamente no CI atual. O repositório está arquivado, usa NDK r10e e baixa dependências sem validar hashes no fluxo analisado. A receita também não fixa o commit do OpenJDK que clona.

## Achados

### [ALTO] Código-fonte OpenJDK não é fixado por commit

**Evidência:** `clonejdk.sh` executa `git clone --depth 1 https://github.com/openjdk/jdk8u openjdk` para Android não-ARMv7. Não há branch, tag ou SHA definido no comando. O resultado depende do estado remoto de `master` no momento da execução.

**Risco:** duas compilações do mesmo commit do wrapper podem incorporar fontes OpenJDK diferentes. Isso impede builds reproduzíveis e dificulta rastrear regressões e vulnerabilidades.

**Correção necessária:** selecionar uma revisão JDK 8u específica, fixar SHA completo, verificar assinatura/proveniência quando disponível e registrar o SHA no manifesto do artefato. Não usar `master` móvel.

### [ALTO] Falhas ao aplicar patches são ignoradas

**Evidência:** `buildjdk.sh` executa `git apply --reject ... || echo "git apply failed"` para os patches Android. O script continua mesmo se um patch falhar parcialmente.

**Risco:** o build pode prosseguir com código parcialmente modificado e produzir um JRE inconsistente, ou mascarar incompatibilidades entre a revisão OpenJDK e os patches.

**Correção necessária:** validar cada patch antes do build, aplicar com falha fatal, conferir árvore limpa e registrar os hashes dos patches. Nunca converter falha de patch em aviso não fatal.

### [ALTO] Dependências externas sem verificação de integridade

**Evidência:** `getlibs.sh` baixa FreeType e CUPS via `wget` e extrai diretamente; `ci_build_global.sh` baixa NDK r10e do Google e extrai o ZIP. Os scripts analisados não validam SHA-256 ou assinatura desses arquivos antes da extração.

**Risco:** artefatos alterados, mirror comprometido ou resposta inesperada podem entrar no processo de build.

**Correção necessária:** manter versões e hashes SHA-256 aprovados em manifesto versionado, verificar antes de extrair e falhar se o hash divergir. Preferir origens oficiais e downloads imutáveis.

### [ALTO] Sessão remota tmate no workflow de build

**Evidência:** `.github/workflows/build.yml` inicia `mxschmitt/action-tmate@v3` quando o job falha.

**Risco:** uma sessão interativa remota em workflow de build aumenta a superfície de acesso ao runner. Em especial, não é apropriado manter esse mecanismo em pipelines que possam receber contribuições externas ou segredos.

**Correção necessária:** remover o passo tmate; usar logs, artefatos de diagnóstico sanitizados e reruns controlados. Fixar actions por SHA completo e aplicar permissões mínimas.

### [MÉDIO] Toolchain histórica e dependência de ambiente obsoleto

**Evidência:** README exige Android NDK r10e e afirma que outras versões causam falhas; `maketoolchain.sh` usa `make-standalone-toolchain.sh`, `--platform=android-21`, GCC e sysroot da geração antiga do NDK. O CI declara Ubuntu 22.04, mas a documentação histórica não prova compatibilidade desse conjunto com o host atual.

**Risco:** dificuldade de reproduzir, dependências sem suporte e incompatibilidades com bibliotecas/headers do Android moderno.

**Correção necessária:** executar build isolado e reproduzível com imagem de host fixada; avaliar portabilidade para NDK suportado sem trocar a toolchain às cegas. Se o NDK antigo for indispensável, isolá-lo e documentar riscos e hashes.

### [MÉDIO] Pipeline repete build automaticamente após falha

**Evidência:** `buildjdk.sh` tenta `make JOBS=4 images`; em caso de falha, tenta novamente sem uma etapa explícita de limpeza ou diagnóstico da causa.

**Risco:** pode esconder falhas intermitentes ou deixar estado parcial no diretório de build.

**Correção necessária:** falhar com logs completos e reproduzir em workspace limpo; retries só para falhas transitórias classificadas, com limite e evidência.

### [MÉDIO] Empacotamento depende de caminhos e ferramentas legadas

**Evidência:** `tarjdk.sh` usa caminho de strip legado via variável `NDK_PREBUILT_ARCH`, executa limpeza ELF externa e empacota saídas sem manifesto de proveniência ou verificação final de ABI/dependências dinâmicas.

**Risco:** runtime pode ser empacotada com biblioteca incompatível, dependência ausente ou binário de arquitetura errada.

**Correção necessária:** verificar cada ELF com ferramentas apropriadas, arquitetura, API Android, dependências compartilhadas e hashes; gerar SBOM/manifestações de licença e checksum do arquivo final.

### [MÉDIO] Licenciamento e proveniência não estão consolidados no wrapper

**Evidência:** a API do repositório wrapper não declara licença SPDX e o fluxo combina OpenJDK, patches, FreeType, CUPS, fontes e ferramentas de terceiros. O repositório OpenJDK 8u declara GPL-2.0, com obrigações adicionais aplicáveis aos componentes distribuídos.

**Risco:** não há base suficiente para redistribuir um pacote binário sem inventário de componentes, avisos e análise de licenças de cada dependência.

**Correção necessária:** produzir inventário de componentes, versões, licenças e avisos; preservar arquivos de copyright e cumprir GPLv2 e demais licenças antes de publicar binários.

## O que foi confirmado

- A receita histórica lista Android AArch64 como `aarch64-linux-android`.
- O wrapper seleciona JVM `server` para AArch64 por padrão.
- O README exige NDK r10e e API de toolchain Android 21.
- O wrapper clona `openjdk/jdk8u` sem SHA fixo.
- O wrapper tenta aplicar patches com falha não fatal.
- O workflow contém etapa tmate condicional a falha.
- O empacotamento altera e reduz a imagem JRE; precisa de validação funcional depois do build.

## Decisão para Mikael Runtime 8

**Não copiar nem executar o pipeline histórico diretamente.** Usá-lo como referência técnica para identificar patches Android e requisitos de ABI. A base deve ser reavaliada com fonte JDK 8u fixada, patches revisados, dependências verificadas e build isolado.

## Atualização do patch principal

O diff principal foi recuperado integralmente por SHA. Seu inventário tem 207 caminhos, 58.398 linhas adicionadas e 114 removidas. A revisão e os achados estão em [OPENJDK8_ANDROID_PATCH_REVIEW.md](OPENJDK8_ANDROID_PATCH_REVIEW.md), [OPENJDK8_PATCH_FINDINGS.md](OPENJDK8_PATCH_FINDINGS.md) e [OPENJDK8_PATCH_INVENTORY.md](OPENJDK8_PATCH_INVENTORY.md). O patch não foi aprovado para integração direta.

## Próximas ações de engenharia

1. Corrigir os achados registrados em OPENJDK8_PATCH_FINDINGS.md e adicionar testes de regressão.
2. Escolher e fixar a revisão exata do OpenJDK 8u e validar compatibilidade dos patches.
3. Montar manifesto de dependências com hashes e licenças.
4. Remover tmate e qualquer download sem verificação antes de criar CI de build.
5. Fazer build de prova em ambiente isolado e testar `java -version`, JNI, bibliotecas ELF e execução real no Android ARM64.
6. Só depois integrar o artefato ao empacotador MultiRT do CS Launcher Plus.

## Referências examinadas

- Wrapper e scripts: https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/tree/buildjre8
- Commit auditado do wrapper: https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/commit/04b90441da7e9649cb6508a037423f08d1fc531f
- Script de clone OpenJDK: https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/blob/buildjre8/clonejdk.sh
- Script de patches/build: https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/blob/buildjre8/buildjdk.sh
- Workflow CI: https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch/blob/buildjre8/.github/workflows/build.yml
- OpenJDK 8u: https://github.com/openjdk/jdk8u
