#!/usr/bin/env python3
"""Validate the Minecraft 1.12.2 compatibility contract for Mikael Runtime 8."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path("config/compatibility-minecraft-1.12.2.json")
REQUIRED_TOP = {
    "schemaVersion", "status", "target", "optifine", "modLoading",
    "modpacks", "native", "launchers", "acceptanceStages", "limitations",
}


def validate_compatibility(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["A raiz do contrato precisa ser um objeto JSON."]

    missing = sorted(REQUIRED_TOP - data.keys())
    extra = sorted(data.keys() - REQUIRED_TOP)
    if missing:
        errors.append("Campos ausentes: " + ", ".join(missing))
    if extra:
        errors.append("Campos desconhecidos: " + ", ".join(extra))
    if missing:
        return errors

    if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1:
        errors.append("schemaVersion precisa ser o inteiro 1.")
    if data["status"] != "target-not-yet-verified":
        errors.append("O status deve permanecer target-not-yet-verified até testes reais.")

    target = data["target"]
    if not isinstance(target, dict):
        errors.append("target precisa ser um objeto.")
        target = {}
    expected_target = {
        "minecraftVersion": "1.12.2",
        "javaMajor": 8,
        "maximumClassFileMajorVersion": 52,
        "architecture": "aarch64",
        "forgeVersion": "14.23.5.2864",
    }
    for key, expected in expected_target.items():
        if target.get(key) != expected or type(target.get(key)) is not type(expected):
            errors.append(f"target.{key} precisa ser {expected!r}.")

    optifine = data["optifine"]
    if not isinstance(optifine, dict):
        errors.append("optifine precisa ser um objeto.")
    else:
        if optifine.get("enabledAsOptionalLayer") is not True:
            errors.append("OptiFine precisa permanecer uma camada opcional.")
        if optifine.get("referenceBuild") != "HD_U_G5":
            errors.append("A build de referência do OptiFine precisa ser HD_U_G5.")
        if optifine.get("requiresForgeCombinationTest") is not True:
            errors.append("A combinação Forge + OptiFine precisa de teste explícito.")

    mod_loading = data["modLoading"]
    if not isinstance(mod_loading, dict):
        errors.append("modLoading precisa ser um objeto.")
    else:
        required_true = (
            "legacyLaunchWrapper", "preserveLauncherClasspathOrder",
            "doNotFilterModLibraries", "resolveDependenciesThroughLauncher",
        )
        if mod_loading.get("loader") != "Forge Mod Loader":
            errors.append("modLoading.loader precisa ser Forge Mod Loader.")
        for key in required_true:
            if mod_loading.get(key) is not True:
                errors.append(f"modLoading.{key} precisa ser true.")

    modpacks = data["modpacks"]
    if not isinstance(modpacks, dict):
        errors.append("modpacks precisa ser um objeto.")
    else:
        for key in (
            "allowMultipleMods", "preserveGameDirectory",
            "preserveConfigAndOverrides", "preserveAllDeclaredLibraries",
            "checkNativeLibraryAbi", "largeClasspathMustBeMeasured",
        ):
            if modpacks.get(key) is not True:
                errors.append(f"modpacks.{key} precisa ser true.")

    native = data["native"]
    if not isinstance(native, dict):
        errors.append("native precisa ser um objeto.")
    else:
        if native.get("requiredAbi") != "aarch64":
            errors.append("native.requiredAbi precisa ser aarch64.")
        if native.get("jniRequired") is not True:
            errors.append("JNI precisa estar marcado como obrigatório.")
        if native.get("lwjglNativeLibraries") != "provided-and-extracted-by-launcher":
            errors.append("As bibliotecas nativas LWJGL precisam ser fornecidas e extraídas pelo launcher.")
        if native.get("graphicsRenderer") != "provided-by-launcher":
            errors.append("O renderizador gráfico precisa ser fornecido pelo launcher.")

    launchers = data["launchers"]
    if not isinstance(launchers, list) or not all(isinstance(item, str) for item in launchers) or not {"FCL", "CS Launcher Plus"}.issubset(launchers):
        errors.append("launchers precisa incluir FCL e CS Launcher Plus.")

    stages = data["acceptanceStages"]
    required_stages = {
        "minecraft-1.12.2-vanilla", "forge-14.23.5.2864",
        "optifine-hd-u-g5-alone", "forge-plus-optifine-hd-u-g5",
        "small-mod-set", "large-modpack", "launcher-fcl",
        "launcher-cs-launcher-plus",
    }
    if not isinstance(stages, list) or not all(isinstance(item, str) for item in stages) or not required_stages.issubset(stages):
        errors.append("acceptanceStages não contém todas as etapas obrigatórias.")

    limitations = data["limitations"]
    if not isinstance(limitations, list) or len(limitations) < 4 or not all(
        isinstance(item, str) and item.strip() for item in limitations
    ):
        errors.append("limitations precisa documentar as limitações de compatibilidade.")

    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERRO: não foi possível ler JSON válido em {path}: {exc}", file=sys.stderr)
        return 2

    errors = validate_compatibility(data)
    if errors:
        for error in errors:
            print(f"ERRO: {error}", file=sys.stderr)
        return 1
    print(f"Contrato de compatibilidade válido: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
