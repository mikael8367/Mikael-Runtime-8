# Formato do perfil de execução

O arquivo `config/minecraft-1.12.2.json` descreve apenas parâmetros do perfil. Ele não contém a JVM, bibliotecas nativas, JNI ou integração com o launcher.

## Campos obrigatórios

- `profileVersion`: versão inteira do formato.
- `javaMajor`: deve ser 8 para Minecraft 1.12.2.
- `architecture`: alvo inicial `aarch64`.
- `minecraftVersion` e `forgeVersion`: versões exatas testadas.
- `memory.initialHeapMb` e `memory.maximumHeapMb`: limites do heap em MiB.
- `jvmArguments`: argumentos JVM sem duplicatas; `-Xms` e `-Xmx` devem corresponder aos valores de memória.
- `status`: permanece `experimental-profile-only` até existir uma runtime executável e validada.
- `warning`: aviso explícito de que o perfil não instala uma JVM.

## Guardrails atuais

O validador rejeita:
- versão Java ou arquitetura diferentes do alvo;
- heap inicial inferior a 256 MiB;
- heap máximo menor que o inicial ou superior a 3072 MiB;
- argumentos de heap ausentes, duplicados, malformados ou divergentes dos campos de memória;
- chaves não reconhecidas, para evitar erros silenciosos de digitação.

Esses limites são guardrails de configuração, não uma recomendação de memória para todo aparelho. O valor final deve ser ajustado com testes reais no dispositivo e no conjunto de mods.

## Executar validação

```bash
python scripts/validate_profile.py
python -m unittest discover -s tests -v
```

O GitHub Actions executa os mesmos comandos em cada push e pull request para `main`.
