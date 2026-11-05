# Matriz de testes pendentes — Mikael Runtime 8

Esta matriz transforma os achados estáticos do patch Android OpenJDK 8 em critérios verificáveis. Nenhum teste abaixo está marcado como aprovado: a runtime ainda não foi compilada.

## 1. Conversão de texto e locale

| Caso | Entrada/condição | Resultado esperado |
|---|---|---|
| UTF-8 ASCII | texto comum | saída idêntica |
| UTF-8 NUL | U+0000 no meio do texto | conversão termina e consome o byte |
| UTF-8 inválido | sequência malformada em modo estrito | erro definido, sem avanço indevido |
| UTF-8 inválido | modos IGNORE e TRANSLIT | cursor e contadores permanecem válidos |
| UTF-16 | BMP e pares substitutos válidos | conversão correta |
| UTF-16 | substituto isolado ou par inválido | erro definido |
| UTF-32 | valores válidos e fora do intervalo Unicode | conversão correta ou erro |
| Locale | pt-BR, en-US e locale ausente | datas, números e charset documentados |

## 2. HotSpot, memória e sinais

- Inicialização e encerramento repetidos.
- Alocação sob pressão de heap e coleta repetida.
- Threads concorrentes com bloqueios, interrupções e encerramento.
- Tratamento de sinais e page trap.
- Cópia de memória em limites de página, buffers alinhados e desalinhados.
- Verificação de ausência de deadlock, corrupção e crash.
- Medição de pausas de GC e consumo de memória.

## 3. JNI e bibliotecas nativas

- Carregar, chamar e descarregar bibliotecas JNI ARM64.
- Verificar símbolos e dependências ELF.
- Tratar exceções JNI e chamadas concorrentes.
- Repetir carregamento sem duplicar estado ou manter recursos presos.
- Testar bibliotecas ausentes, incompatíveis e com dependências transitivas não encontradas.

## 4. Rede e interfaces

- Enumerar interfaces sem conexão e com conexão.
- IPv4, IPv6, Wi-Fi e dados móveis.
- Múltiplos endereços por interface.
- Interface sem endereço de broadcast.
- Respostas Netlink truncadas, atributos desconhecidos e falhas de socket.
- Garantir liberação de todas as estruturas em caminhos de erro.

## 5. AWT, Java2D e fontes

- Confirmar explicitamente o modo headless esperado.
- Não declarar GLX/X11 disponível sem backend correspondente.
- Carregar fontes padrão e fontes ausentes.
- Renderizar texto e imagens em caminhos suportados.
- Confirmar se componentes AWT são realmente necessários ao Minecraft/FCL.
- Testar inicialização sem DISPLAY e sem servidor X11.

## 6. AArch64, ABI e empacotamento

- Confirmar ELF64 AArch64 para executáveis e bibliotecas.
- Verificar API Android mínima e dependências compartilhadas.
- Validar instruções AArch64 com o assembler escolhido.
- Testar cópia de memória e chamadas JNI no dispositivo ARM64.
- Verificar permissões, symlinks e layout MultiRT após empacotar.
- Executar `java -version` e testes Java básicos no Android 12.

## 7. Minecraft 1.12.2

1. Vanilla 1.12.2 sem mods.
2. Forge 14.23.5.2864 sem mods adicionais.
3. OptiFine isoladamente.
4. Grupos pequenos de mods.
5. Modpack completo somente depois dos testes anteriores.
6. FCL e CS Launcher Plus, com logs de inicialização e encerramento.

## 8. Benchmark

Comparar a runtime candidata com uma runtime de referência no mesmo aparelho, mesma versão do jogo, mesmos mods, mundo, resolução e configurações.

Registrar:
- FPS médio e 1% low;
- RAM máxima e média;
- tempo de inicialização;
- pausas de GC;
- temperatura/condição do aparelho e duração da sessão;
- crashes e logs completos.

Não declarar ganho de FPS sem resultados repetíveis. Estabilidade e compatibilidade são critérios de aprovação anteriores ao desempenho.

## 9. Critério de conclusão

Uma área só pode ser marcada como concluída quando:
- o teste foi executado em ambiente identificado;
- comando, versão e resultado foram registrados;
- falhas foram corrigidas e o teste repetido;
- não há regressão nas áreas dependentes.

A revisão estática e a existência desta matriz não significam que a runtime esteja pronta.
