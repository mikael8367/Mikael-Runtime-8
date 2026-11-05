#!/usr/bin/env python3
"""Validate the experimental Minecraft 1.12.2 Java 8 profile."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = {
    "profileVersion", "name", "javaMajor", "architecture",
    "minecraftVersion", "forgeVersion", "memory", "jvmArguments",
    "status", "warning",
}
HEAP_RE = re.compile(r"^-X(ms|mx)([1-9][0-9]*)([mMgG])$")


def _heap_mb(argument: str, expected_kind: str) -> int:
    match = HEAP_RE.fullmatch(argument)
    if not match or match.group(1) != expected_kind:
        raise ValueError(f"Argumento de heap inválido: {argument!r}")
    amount = int(match.group(2))
    unit = match.group(3).lower()
    return amount * (1024 if unit == "g" else 1)


def validate_profile(profile: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(profile, dict):
        return ["A raiz do perfil precisa ser um objeto JSON."]

    missing = sorted(REQUIRED_TOP_LEVEL - profile.keys())
    extra = sorted(profile.keys() - REQUIRED_TOP_LEVEL)
    if missing:
        errors.append("Campos ausentes: " + ", ".join(missing))
    if extra:
        errors.append("Campos desconhecidos: " + ", ".join(extra))
    if missing:
        return errors

    if type(profile["profileVersion"]) is not int or profile["profileVersion"] != 1:
        errors.append("profileVersion precisa ser o inteiro 1.")
    if type(profile["javaMajor"]) is not int or profile["javaMajor"] != 8:
        errors.append("javaMajor precisa ser 8.")
    if profile["architecture"] != "aarch64":
        errors.append("architecture precisa ser aarch64.")
    if profile["minecraftVersion"] != "1.12.2":
        errors.append("minecraftVersion precisa ser 1.12.2.")
    if not isinstance(profile["name"], str) or not profile["name"].strip():
        errors.append("name não pode ficar vazio.")
    if not isinstance(profile["forgeVersion"], str) or not profile["forgeVersion"].strip():
        errors.append("forgeVersion não pode ficar vazio.")
    if profile["status"] != "experimental-profile-only":
        errors.append("O status deve continuar experimental-profile-only até existir uma runtime testada.")
    if not isinstance(profile["warning"], str) or not profile["warning"].strip():
        errors.append("warning precisa explicar que o perfil não contém a JVM.")

    memory = profile["memory"]
    args = profile["jvmArguments"]
    if not isinstance(memory, dict):
        errors.append("memory precisa ser um objeto.")
        return errors
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        errors.append("jvmArguments precisa ser uma lista de textos.")
        return errors

    for key in ("initialHeapMb", "maximumHeapMb"):
        if type(memory.get(key)) is not int:
            errors.append(f"memory.{key} precisa ser um inteiro.")
    if any(type(memory.get(k)) is not int for k in ("initialHeapMb", "maximumHeapMb")):
        return errors

    initial = memory["initialHeapMb"]
    maximum = memory["maximumHeapMb"]
    if initial < 256:
        errors.append("Heap inicial abaixo do limite mínimo de 256 MiB.")
    if maximum < initial:
        errors.append("Heap máximo não pode ser menor que o heap inicial.")
    if maximum > 3072:
        errors.append("Heap máximo acima do teto experimental de 3072 MiB.")

    xms = [a for a in args if a.startswith("-Xms")]
    xmx = [a for a in args if a.startswith("-Xmx")]
    if len(xms) != 1 or len(xmx) != 1:
        errors.append("Informe exatamente um -Xms e um -Xmx.")
    else:
        try:
            if _heap_mb(xms[0], "ms") != initial:
                errors.append("-Xms não corresponde a memory.initialHeapMb.")
            if _heap_mb(xmx[0], "mx") != maximum:
                errors.append("-Xmx não corresponde a memory.maximumHeapMb.")
        except ValueError as exc:
            errors.append(str(exc))

    if len(args) != len(set(args)):
        errors.append("jvmArguments contém argumentos duplicados.")
    if any(not a.startswith("-") for a in args):
        errors.append("Cada argumento JVM precisa começar com '-'.")
    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config/minecraft-1.12.2.json")
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERRO: não foi possível ler JSON válido em {path}: {exc}", file=sys.stderr)
        return 2

    errors = validate_profile(profile)
    if errors:
        for error in errors:
            print(f"ERRO: {error}", file=sys.stderr)
        return 1
    print(f"Perfil válido: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
