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


## 5. Compatibilidade com mods e modpacks

Consultar [MOD_COMPATIBILITY.md](MOD_COMPATIBILITY.md) e validar o contrato com:

```bash
python scripts/validate_compatibility.py
python -m unittest discover -s tests -p 'test_compatibility.py' -v
```

Sequência obrigatória no Android ARM64:
1. Vanilla 1.12.2.
2. Forge 14.23.5.2864 sem mods adicionais.
3. OptiFine HD U G5 sozinho.
4. Forge + OptiFine HD U G5.
5. Mods em grupos pequenos, incluindo suas dependências.
6. Modpack grande com configs, overrides e todas as bibliotecas preservadas.
7. Repetir os cenários suportados no FCL e no CS Launcher Plus.

Em cada execução, registrar a lista e versão dos mods, classpath efetivo, argumentos JVM, bibliotecas nativas extraídas, renderer, `latest.log` e crash report. Classificar a falha como JVM, launcher, mod conflitante, dependência ausente, ABI nativa ou renderização.

**Não declarar compatibilidade universal:** um contrato validado apenas prova que a estrutura esperada está configurada. Só testes reais demonstram que uma build específica do Forge, OptiFine ou modpack funciona.
