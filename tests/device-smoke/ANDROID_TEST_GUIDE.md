# Teste no Android (sem PC)

Este kit verifica a JVM usada para executar o diagnóstico. O JAR não é a Mikael Runtime 8 e não contém JVM.

## Como obter o kit

1. Abra o repositório no navegador do celular: https://github.com/mikael8367/Mikael-Runtime-8
2. Entre em **Actions**.
3. Abra **Build Android Runtime Test Kit** e selecione a execução mais recente com resultado verde.
4. Em **Artifacts**, baixe `MikaelRuntime8-Device-Test-Kit`.
5. Extraia o ZIP. Ele contém `MikaelRuntimeSmokeTest.jar`, este guia e `SHA256SUMS.txt`.

Se não houver execução verde ou o artefato não aparecer, não use um pacote antigo como se fosse o mais recente.

## Como executar

É necessário um ambiente Android que consiga chamar o executável Java da runtime escolhida. No terminal desse ambiente, entre na pasta extraída e execute:

```sh
java -jar MikaelRuntimeSmokeTest.jar
```

O comando precisa usar a runtime que você quer diagnosticar. Se o terminal estiver usando outra Java, o relatório mostrará isso em `java.home`, `java.version` e `java.class.path`.

## Onde fica o relatório

O programa mostra os resultados na tela e tenta salvar automaticamente:

- primeiro em `user.dir/MikaelRuntime8-device-report.txt`;
- se não conseguir, tenta em `java.io.tmpdir/MikaelRuntime8-device-report.txt`.

No final, ele imprime `REPORT_FILE=` com o caminho encontrado. Envie esse arquivo ou copie toda a saída, incluindo as linhas `[FAIL]` e `RESULT`.

## O que é verificado

- Java 8 e arquitetura ARM64;
- carregamento de classes e reflexão;
- threads e sincronização;
- alocação de memória e métricas de heap/GC;
- leitura e escrita de arquivos UTF-8;
- leitura e escrita de ZIP/JAR;
- diretório temporário gravável;
- presença opcional de LaunchWrapper, Forge e Minecraft no classpath.

As classes de Minecraft/Forge ausentes no classpath do diagnóstico aparecem como `[INFO]`, não como falha.

## Importante

- O resultado descreve somente a runtime que executou o JAR.
- Não comprova que a Mikael Runtime 8 própria funciona: ela ainda precisa ser compilada.
- Não testa renderização GL4ES, LWJGL nativo, OptiFine nem um modpack completo.
- Não instale nem substitua a runtime do launcher com arquivos de teste.
- Um resultado `PASS` não é prova de compatibilidade com Minecraft.

Se o celular não tiver um ambiente que permita executar `java -jar` usando a runtime do launcher, este kit não consegue ser executado diretamente pelo FCL/CS Launcher Plus. Nesse caso, envie o modelo do ambiente disponível e ajustaremos o método sem presumir que o launcher aceite executar JARs arbitrários.
