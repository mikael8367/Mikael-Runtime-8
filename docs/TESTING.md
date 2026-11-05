# Plano de testes e auditoria

## Regra de comparação
Comparar a runtime candidata com a runtime-base no mesmo aparelho, mesma versão do Android, mesmo launcher, mesmo mundo, mesmos mods, mesmas configurações gráficas e mesma duração de teste. Fazer várias execuções e registrar resultados; não comparar sessões com condições diferentes.

## Testes por etapa

### 1. Artefato e arquitetura
- Confirmar que o pacote contém binários ARM64 (aarch64).
- Verificar dependências nativas e bibliotecas compartilhadas.
- Confirmar permissões, caminhos e compatibilidade com a versão Android.
- Verificar hashes e origem dos artefatos.

### 2. JVM
- Executar java -version.
- Compilar e executar um programa Java de teste.
- Testar threads, arquivos, rede local de teste e carregamento de classes.
- Observar encerramentos inesperados e erros de memória.

### 3. Minecraft
- Iniciar 1.12.2 sem mods.
- Iniciar Forge 14.23.5.2864.
- Adicionar mods em grupos pequenos, mantendo cópia dos logs.
- Testar OptiFine isoladamente antes de combinar com outros mods.
- Testar renderização e JNI no ambiente móvel real.

### 4. Métricas
Registrar por execução:
- FPS médio e 1% low, quando a ferramenta permitir.
- RAM máxima e tendência de crescimento.
- Tempo até menu e até mundo carregado.
- Pausas de GC e frequência de coleta, se disponíveis.
- Temperatura/limitação térmica observável.
- Crash, stack trace e latest.log.

## Auditoria de bugs
Antes de marcar uma versão como estável:
- Repetir inicialização e encerramento várias vezes.
- Procurar vazamentos de memória e crescimento contínuo de heap.
- Verificar falhas em caminhos com espaços e permissões Android.
- Verificar incompatibilidade entre ABI e bibliotecas JNI.
- Conferir logs para exceções, avisos de bibliotecas e erros de carregamento.
- Testar configurações padrão e valores ausentes/inválidos.
- Conferir se o perfil não aplica argumentos incompatíveis com a JVM escolhida.
- Não mascarar crashes nem descartar logs necessários para diagnóstico.

## Modelo de relatório

| Campo | Valor |
|---|---|
| Aparelho / Android | |
| ABI | |
| Runtime-base e versão | |
| Runtime candidata e commit | |
| Launcher / versão | |
| Minecraft / Forge | |
| Mods e versões | |
| Configuração gráfica | |
| FPS médio / 1% low | |
| RAM máxima | |
| Tempo de inicialização | |
| Resultado / logs | |
