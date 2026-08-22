#!/usr/bin/env python3
import argparse
from pathlib import Path


MODE_VALUES = {
    "wsl": {
        "runCodexInWindowsSubsystemForLinux": "true",
        "integratedTerminalShell": '"wsl"',
    },
    "powershell": {
        "runCodexInWindowsSubsystemForLinux": "false",
        "integratedTerminalShell": '"powershell"',
    },
}


def update_desktop_section(text: str, values: dict[str, str]) -> str:
    lines = text.splitlines()
    section_start = next(
        (index for index, line in enumerate(lines) if line.strip() == "[desktop]"),
        None,
    )

    if section_start is None:
        if lines and lines[-1] != "":
            lines.append("")
        lines.append("[desktop]")
        section_start = len(lines) - 1
        section_end = len(lines)
    else:
        section_end = next(
            (
                index
                for index in range(section_start + 1, len(lines))
                if lines[index].lstrip().startswith("[")
            ),
            len(lines),
        )

    found: set[str] = set()
    for index in range(section_start + 1, section_end):
        stripped = lines[index].lstrip()
        for key, value in values.items():
            if stripped.startswith(f"{key} =") or stripped.startswith(f"{key}="):
                indent = lines[index][: len(lines[index]) - len(stripped)]
                lines[index] = f"{indent}{key} = {value}"
                found.add(key)

    additions = [f"{key} = {value}" for key, value in values.items() if key not in found]
    lines[section_end:section_end] = additions
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--mode", choices=MODE_VALUES, required=True)
    args = parser.parse_args()

    original = args.config.read_text(encoding="utf-8") if args.config.exists() else ""
    updated = update_desktop_section(original, MODE_VALUES[args.mode])
    if updated != original:
        args.config.parent.mkdir(parents=True, exist_ok=True)
        args.config.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
