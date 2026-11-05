# Formato de runtime do CS Launcher Plus

A runtime Java 8 deve ser distribuída como **arquivo TAR comprimido com XZ** e extensão final `.tar.xz`. Não renomeie um ZIP ou JAR para essa extensão: o conteúdo precisa ser realmente TAR+XZ.

## Estrutura obrigatória na raiz do arquivo

O launcher extrai o conteúdo do arquivo diretamente para a pasta da runtime. Portanto, os caminhos devem começar na raiz da JRE, sem uma pasta externa como `jre/`:

```text
bin/java
release
lib/rt.jar
lib/aarch64/server/libjvm.so
lib/...
```

O CS Launcher Plus lê `release` para detectar `JAVA_VERSION` e `OS_ARCH`, e espera a biblioteca HotSpot no diretório `lib/aarch64/server/`. O nome exibido/instalado da runtime é definido pelo gerenciador do launcher; o nome do arquivo não substitui esses metadados.

## Arquivo produzido pelo projeto

`Mikael-Runtime-8-Android-ARM64.tar.xz`

O empacotador verifica:
- extensão `.tar.xz` e leitura real como TAR+XZ;
- ausência de caminhos duplicados, absolutos ou que escapem da raiz;
- estrutura plana da JRE, sem diretório externo;
- metadados Java 8 e ARM64;
- `bin/java` executável e ELF64/AArch64;
- `lib/aarch64/server/libjvm.so`, `lib/rt.jar` e bibliotecas nativas ARM64.

O ZIP que o GitHub pode fornecer ao baixar um artifact é apenas o invólucro do download do Actions. Dentro dele fica o arquivo real `.tar.xz` da runtime.

A validação do arquivo não comprova que a JVM executa no Android. Ainda são necessários testes no aparelho com Java, JNI, GC, FCL/CS Launcher Plus e Minecraft 1.12.2.
