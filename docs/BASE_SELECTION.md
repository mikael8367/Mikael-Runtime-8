# Seleção da base Java 8 para Android

## Candidato investigado

Foi inspecionado o repositório público [PojavLauncherTeam/android-openjdk-build-multiarch](https://github.com/PojavLauncherTeam/android-openjdk-build-multiarch), branch `buildjre8`.

O README descreve uma compilação OpenJDK 8 para Android ARM64/AArch64, mas também:
- O repositório foi arquivado em 19 de maio de 2025.
- O procedimento documentado exige Android NDK r10e.
- O próprio README alerta que versões de NDK diferentes causam erros de compilação.
- A receita é antiga e precisa ser reproduzida antes de ser considerada utilizável.

## Decisão

**Não copiar nem adotar esse projeto como base de produção ainda.** Ele comprova que existiu uma rota de compilação OpenJDK 8 para Android ARM64, mas seu estado arquivado e a dependência de uma toolchain antiga tornam arriscado tratá-lo como solução pronta.

O projeto Mikael Runtime 8 deve primeiro reproduzir a compilação em ambiente isolado e documentar:
1. Commit exato da fonte OpenJDK usada.
2. Licenças e avisos de cada componente.
3. Ferramentas e versões necessárias.
4. Se o binário gerado realmente executa no Android 12 ARM64.
5. Se JNI e bibliotecas nativas necessárias ao Minecraft funcionam.
6. Se a solução pode ser mantida sem depender de ferramentas obsoletas ou inseguras.

## ABI

O alvo do projeto é Android `arm64-v8a` (AArch64). A documentação do Android NDK identifica `arm64-v8a` como ABI de 64 bits para processadores AArch64. Isso não significa que qualquer binário Linux AArch64 seja compatível com Android: sistema operacional, ABI, bibliotecas e nível de API também precisam corresponder.

## Próxima decisão técnica

Antes de implementar patches ou scripts de compilação, comparar:
- A receita histórica do projeto Pojav.
- A possibilidade de manter/portar a fonte OpenJDK 8 para uma toolchain Android suportada.
- A compatibilidade com a interface de runtime esperada pelo FCL.

Nenhuma fonte foi incorporada a este repositório e nenhum binário de terceiros foi copiado.
