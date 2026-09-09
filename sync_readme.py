#!/usr/bin/env python3
"""Aktualisiert den automatisch gepflegten Projektstatus in README.md."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
readme = ROOT / "README.md"
source = ROOT / "dj_set_sorter.py"

text = readme.read_text(encoding="utf-8")
lines = source.read_text(encoding="utf-8").splitlines()
functions = sum(1 for line in lines if line.startswith("def "))
classes = sum(1 for line in lines if line.startswith("class "))
files = sorted(p.name for p in ROOT.iterdir() if p.is_file() and p.name not in {"README.md", ".gitignore"} and not p.name.startswith("."))
status = (
    "## Automatisch gepflegter Projektstatus\n\n"
    f"- Hauptprogramm: `{source.name}`\n"
    f"- Python-Funktionen: **{functions}**\n"
    f"- Python-Klassen: **{classes}**\n"
    f"- Projektdateien: {', '.join(f'`{x}`' for x in files)}\n"
)
marker = r"## Automatisch gepflegter Projektstatus\n\n.*?(?=\n## |\Z)"
if re.search(marker, text, flags=re.S):
    text = re.sub(marker, status.rstrip(), text, flags=re.S)
else:
    text = text.rstrip() + "\n\n" + status
readme.write_text(text.rstrip() + "\n", encoding="utf-8")
