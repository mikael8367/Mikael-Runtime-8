# Compatibilidade com mods, OptiFine e modpacks — Minecraft 1.12.2

## Objetivo

O primeiro alvo de compatibilidade da Mikael Runtime 8 é Minecraft Java 1.12.2 em Java 8 ARM64, com Forge 14.23.5.2864. A camada de execução deve permitir que o launcher carregue os mods e suas dependências sem a runtime filtrar ou alterar o classpath.

O contrato técnico está em `config/compatibility-minecraft-1.12.2.json` e é validado por `scripts/validate_compatibility.py`.

## Alvos de teste

- Minecraft 1.12.2 Vanilla.
- Forge 14.23.5.2864.
- OptiFine HD U G5 sozinho.
- Forge 14.23.5.2864 + OptiFine HD U G5.
- Conjunto pequeno de mods Forge 1.12.2.
- Modpack grande, com todas as bibliotecas e dependências declaradas.
- FCL e CS Launcher Plus.

OptiFine é uma camada opcional. A combinação Forge + OptiFine será validada separadamente porque a compatibilidade depende das builds exatas e dos outros mods instalados.

## Requisitos da JVM/runtime

1. Java 8 e suporte a bytecode até class-file major version 52.
2. ARM64/AArch64 para a JVM e todas as bibliotecas nativas carregadas dentro do processo.
3. JNI funcional, incluindo carregamento e descarregamento de bibliotecas.
4. Class loader Java 8 e APIs padrão necessárias a LaunchWrapper, Forge, ASM e mods 1.12.2.
5. Threads, reflexão, recursos, arquivos, ZIP/JAR e rede funcionais.
6. Não adicionar flags experimentais de GC/JIT sem confirmar que a VM escolhida as reconhece e sem testes de estabilidade.

## Requisitos do launcher

A runtime não substitui o launcher. FCL/CS Launcher Plus continuam responsáveis por:

- montar o classpath e preservar sua ordem;
- resolver e baixar as dependências do Forge e dos mods;
- disponibilizar os arquivos do jogo, assets e diretório de configuração;
- extrair as bibliotecas nativas LWJGL adequadas ao Android/ARM64;
- fornecer o backend gráfico usado pelo dispositivo (por exemplo, GL4ES, quando suportado);
- passar argumentos de inicialização corretos para Minecraft, Forge e OptiFine.

Não remover JARs, bibliotecas ou dependências de mods para tentar reduzir memória. Modpacks grandes também precisam de teste de tamanho do classpath, limite de argumentos do processo Android, tempo de inicialização e RAM.

## Regras de compatibilidade de modpacks

- Preservar todos os JARs e dependências declarados pelo launcher.
- Não alterar a ordem de classpath exigida pelo Forge/LaunchWrapper.
- Preservar o diretório do jogo, configs, scripts, recursos e overrides do modpack.
- Verificar que bibliotecas nativas são ARM64 e compatíveis com Android.
- Registrar o conjunto exato de mods e versões em cada teste.
- Separar falha da JVM, falha do launcher, conflito entre mods e limitação do renderizador.

## Ordem obrigatória de validação

1. Vanilla 1.12.2.
2. Forge 14.23.5.2864 sem mods extras.
3. OptiFine HD U G5 sozinho.
4. Forge + OptiFine HD U G5.
5. Mods em grupos pequenos, adicionando dependências junto.
6. Modpack completo.
7. Repetir no FCL e no CS Launcher Plus.

Em cada etapa guardar `latest.log`, crash report, argumentos JVM, lista de mods, versão do launcher, versão do Android e arquitetura das bibliotecas nativas.

## Limites e promessa de compatibilidade

Não existe garantia técnica de que uma JVM torne todos os mods compatíveis entre si. Alguns mods têm conflitos próprios, dependem de versões específicas, usam bibliotecas nativas não disponíveis no Android ou exigem renderizadores incompatíveis.

O estado do contrato permanece `target-not-yet-verified` até a runtime real ser compilada e passar por todos os estágios em Android ARM64. A existência deste contrato e seus testes de validação não significa que Forge, OptiFine ou qualquer modpack já tenha sido executado com a Mikael Runtime 8.
