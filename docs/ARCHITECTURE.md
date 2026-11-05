# Arquitetura da Mikael Runtime 8

## Objetivo
Construir uma distribuição Java 8 para Android ARM64, testável com Minecraft Java 1.12.2 Forge. O foco inicial é compatibilidade e estabilidade; desempenho só será considerado melhor quando medições reproduzíveis demonstrarem isso.

## O que é e o que não é
- **Runtime/JRE:** conjunto formado por máquina virtual, bibliotecas Java, bibliotecas nativas e arquivos de suporte.
- **JVM:** executa bytecode Java e implementa gerenciamento de memória, carregamento de classes, threads e interfaces nativas.
- **Launcher:** configura e inicia a JVM; não substitui a JVM.

Um aplicativo de configuração ou um conjunto de flags não constitui uma JVM nova.

## Estratégia técnica
A primeira versão deve partir de uma implementação OpenJDK 8 cuja origem, licença, suporte ARM64 e viabilidade de compilação para Android sejam confirmados. Não será escrita uma JVM do zero nesta etapa: isso exigiria implementar bytecode verifier, class loader, interpretador/JIT, garbage collector, JNI, threads e bibliotecas padrão.

Antes de escolher uma distribuição-base, registrar:
1. URL oficial do código-fonte e versão exata.
2. Licença e avisos obrigatórios.
3. Alvos Android/API e ABI realmente suportados.
4. Ferramentas de compilação e patches necessários.
5. Testes que comprovem execução no Android de destino.

## Componentes
- **VM:** implementação Java 8 ARM64 validada.
- **Bibliotecas:** módulos Java e bibliotecas nativas compatíveis com Android.
- **Camada JNI:** integração entre Java e bibliotecas nativas usadas pelo jogo.
- **Perfil Minecraft:** parâmetros de memória e inicialização separados da VM.
- **Integração FCL:** documentação de seleção e instalação manual somente após existir um pacote válido.
- **Aplicativo próprio:** interface futura para gerenciar perfis e diagnósticos; não faz parte do primeiro marco.

## Limites de compatibilidade
Minecraft 1.12.2 Forge pode depender de bibliotecas JNI, renderizadores e particularidades do launcher. Uma JVM iniciar não prova que o jogo, Forge, OptiFine ou GL4ES funcionarão. Cada camada precisa ser testada separadamente.

## Fluxo planejado
1. Validar a origem OpenJDK 8 e o alvo Android ARM64.
2. Construir um protótipo mínimo e verificar sua execução no Android.
3. Testar ferramentas Java e bibliotecas padrão.
4. Testar inicialização de Minecraft 1.12.2 sem mods.
5. Testar Forge e depois conjuntos de mods controlados.
6. Medir FPS, memória, pausas de GC, tempo de inicialização e falhas.
7. Só então preparar integração com FCL e distribuição.
