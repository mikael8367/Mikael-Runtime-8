# Teste no Android (sem PC)

Este kit permite verificar funções básicas de uma JRE Java 8 ARM64 candidata diretamente no Android. O JAR é um diagnóstico, não é a Mikael Runtime 8 e não contém JVM.

## Como obter o JAR

1. Abra a aba **Actions** do repositório.
2. Execute o workflow **Build Android Runtime Test Kit** ou abra a execução mais recente.
3. Em **Artifacts**, baixe `MikaelRuntime8-Device-Test-Kit`.
4. Extraia o ZIP no celular.

## Como executar

Use uma runtime Java 8 ARM64 já instalada no FCL/CS Launcher Plus para o teste preliminar. Abra um terminal que consiga executar o binário Java dessa runtime e rode:

```sh
java -jar MikaelRuntimeSmokeTest.jar
```

Se o launcher permitir argumentos Java personalizados, pode-se usar o JAR como classe principal de diagnóstico. O relatório imprime propriedades da VM e o resultado de cada teste.

## O que é verificado

- Java 8 e arquitetura ARM64;
- carregamento de classes e reflexão;
- threads e sincronização;
- alocação de memória e chamada de GC;
- leitura/escrita de arquivos UTF-8;
- leitura/escrita de ZIP/JAR;
- visibilidade opcional de LaunchWrapper, Forge e Minecraft no classpath do processo.

As verificações de LaunchWrapper/Forge/Minecraft são informativas quando esses JARs não estão no classpath do processo de diagnóstico.

## Limitações

- O teste com uma runtime existente verifica o ambiente atual, não uma JVM Mikael Runtime 8 própria.
- O kit não testa renderização GL4ES, LWJGL nativo, OptiFine ou compatibilidade completa de modpacks.
- A runtime própria ainda precisa ser compilada antes de poder ser selecionada e testada.
- Não use resultado PASS deste kit como prova de compatibilidade do Minecraft.

Guarde a saída completa e envie o texto ou arquivo do relatório para análise.
