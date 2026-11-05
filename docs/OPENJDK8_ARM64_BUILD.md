# Etapa de compilação OpenJDK 8 ARM64

## Objetivo

Preparar uma JRE Java 8 Android `arm64-v8a` para a Mikael Runtime 8. O alvo inicial é Minecraft Java 1.12.2; compatibilidade com Forge, OptiFine, mods e modpacks só será declarada após testes no Android.

## Primeira barreira automatizada

O workflow [OpenJDK 8 ARM64 source preflight](../.github/workflows/openjdk8-arm64-preflight.yml) faz uma verificação anterior à compilação:

1. Busca a receita Android em um commit imutável do repositório Pojav.
2. Busca o OpenJDK 8u em um commit imutável (base 8u312).
3. Confirma os SHAs efetivamente baixados.
4. Verifica e aplica os patches Android com falha fatal; não aceita aplicação parcial.
5. Confere a presença da árvore de código AArch64 e registra a proveniência em um artefato de diagnóstico.

Revisões fixadas:
- Receita Android: `04b90441da7e9649cb6508a037423f08d1fc531f`
- OpenJDK 8u: `7fdf5cd77f209427758437d7e147ea1c18b4ec35`

## Por que a primeira execução é uma pré-verificação

A receita histórica depende do Android NDK r10e e de bibliotecas nativas antigas. O wrapper original também contém downloads sem verificação de integridade e comandos que ignoram falhas de patch. Não é correto executar esse pipeline integralmente antes de validar a correspondência entre a fonte fixada e os patches.

O workflow atual **não compila a JVM nem produz JRE**. Ele confirma se a combinação de fonte e patches é tecnicamente aplicável. Se falhar, o log deve ser corrigido antes de habilitar a compilação completa.

## Critérios para liberar o build completo

- [ ] A pré-verificação de patches passa sem rejeições.
- [ ] Fixar e verificar a integridade do NDK r10e e das dependências nativas.
- [ ] Substituir os passos legados de build por comandos com falha fatal e logs preservados.
- [ ] Compilar HotSpot Server AArch64 e bibliotecas Java.
- [ ] Verificar todos os ELF: arquitetura AArch64, ABI Android, API mínima e dependências dinâmicas.
- [ ] Empacotar JRE com manifesto de proveniência, licenças e SHA-256.
- [ ] Executar `java -version`, smoke tests, JNI, threads, GC e carregamento de bibliotecas no Android real.
- [ ] Testar Minecraft 1.12.2 Vanilla, Forge, OptiFine, Forge+OptiFine e modpack.

## Limites

Um build verde de CI não prova execução no telefone. Binários AArch64 Linux genéricos não são automaticamente compatíveis com Android/Bionic. A runtime também não fornece LWJGL, GL4ES, assets, classpath ou loader de mods: esses componentes continuam sob responsabilidade do launcher e do ambiente gráfico.

Nenhum APK é produzido nesta etapa.

## Como acompanhar a validação no celular

1. Abra [Actions](https://github.com/mikael8367/Mikael-Runtime-8/actions).
2. Entre em **OpenJDK 8 ARM64 source preflight**.
3. Abra a execução mais recente e confira se o job `source-preflight` terminou como `success`.
4. Em **Artifacts**, baixe `MikaelRuntime8-OpenJDK8-ARM64-Preflight`.
5. Dentro do ZIP, confira `openjdk-source-preflight.txt`, `android-patch-diff-stat.txt` e `android-patch-files.txt`.

Se o job falhar, abra o job e copie o trecho do primeiro passo vermelho e o erro completo. Não tente compilar ou instalar os patches manualmente no celular.

**O que esse teste permite concluir:** se as revisões fixadas foram baixadas e os dois patches principais aplicaram sequencialmente à árvore OpenJDK selecionada, sem rejeições.

**O que ainda não permite concluir:** não compila a JVM, não gera `.tar.xz`, não prova que o HotSpot inicia no Android e não testa Minecraft/Forge/OptiFine. Para isso, ainda precisamos concluir a toolchain e o build ARM64 real.
