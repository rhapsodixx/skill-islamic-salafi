#!/usr/bin/env python3
"""Local + CI gate. Usage: python3 scripts/check.py [--root PATH]"""
import argparse, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

SKILL = "islamic-salafi"
COLL = r"(Bukhari|Muslim|Abu Dawud|Tirmidhi|Nasa'i|Ibn Majah|Ahmad)"
NUM = r"\s+(?:no\.?|nomor)\s*(\d+)"
ITEM = COLL + NUM
HR = re.compile(r"HR\.?\s*" + ITEM + r"(?:\s*,\s*" + ITEM + r")*", re.I)
ITEM_RE = re.compile(ITEM, re.I)
QA = re.compile(r"islamqa\.info\s+fatwa" + NUM, re.I)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def char_len(text: str) -> int:
    return len(text)


def strip_frontmatter(text: str) -> str:
    text = text.lstrip("﻿").replace("\r\n", "\n")
    m = re.match(r"---\n.*?\n---\n?", text, re.S)
    return text[m.end():] if m else text


def find_citations(text: str) -> list[str]:
    found = []  # (position, citation)
    for m in QA.finditer(text):
        found.append((m.start(), f"islamqa {m.group(1)}"))
    for m in HR.finditer(text):
        for i in ITEM_RE.finditer(m.group(0)):
            found.append((m.start() + i.start(), f"{i.group(1).lower()} {i.group(2)}"))
    return [c for _, c in sorted(found)]


def find_agentskills(root: Path):
    # fall back to .venv of the target root, then of this script's own repo
    for r in (root, Path(__file__).resolve().parent.parent):
        if (r / ".venv/bin/agentskills").exists():
            return shutil.which("agentskills") or str(r / ".venv/bin/agentskills")
    return shutil.which("agentskills")


def run_checks(root: Path) -> list[str]:
    errs = []
    skill_dir = root / "skills" / SKILL
    skill_md = skill_dir / "SKILL.md"

    # 1, 2: name + description via validator
    exe = find_agentskills(root)
    if not exe:
        errs.append("agentskills not found: pip install skills-ref")
    else:
        r = subprocess.run([exe, "read-properties", str(skill_dir)], capture_output=True, text=True)
        try:
            props = json.loads(r.stdout)
        except ValueError:
            errs.append(f"{skill_md}: agentskills read-properties failed: {(r.stderr or r.stdout).strip()}")
            props = None
        if props:
            if props.get("name") != SKILL:
                errs.append(f"{skill_md}: name {props.get('name')!r} != folder {SKILL!r}")
            n = char_len(props.get("description", ""))
            if n > 1024:
                errs.append(f"{skill_md}: description is {n} chars (max 1024)")

    # 3: body size; 4: references exist
    skill_text = read(skill_md)
    body = strip_frontmatter(skill_text)
    if char_len(body) > 8000:
        errs.append(f"{skill_md}: SKILL.md body is {char_len(body)} chars (max 8000)")
    if len(body.splitlines()) > 500:
        errs.append(f"{skill_md}: SKILL.md body is {len(body.splitlines())} lines (max 500)")
    for ref in sorted(set(re.findall(r"references/([\w.-]+\.md)", skill_text))):
        if not (skill_dir / "references" / ref).is_file():
            errs.append(f"{skill_md}: references/{ref} does not exist")

    # 5: plugin json
    for j in sorted((root / ".claude-plugin").glob("*.json")):
        try:
            json.loads(read(j))
        except ValueError as e:
            errs.append(f"{j}: invalid JSON: {e}")

    # 6: persona
    persona = root / "persona" / "islamic-adab.md"
    if persona.exists():
        t = read(persona)
        if char_len(t) > 1500:
            errs.append(f"{persona}: islamic-adab.md is {char_len(t)} chars (max 1500)")
        for mk in ("<!-- islamic-adab:start -->", "<!-- islamic-adab:end -->"):
            if mk not in t:
                errs.append(f"{persona}: islamic-adab.md missing marker {mk}")

    # 7: chatgpt bundle
    instr = root / "chatgpt" / "instructions.md"
    if instr.exists() and char_len(read(instr)) > 8000:
        errs.append(f"{instr}: chatgpt/instructions.md is {char_len(read(instr))} chars (max 8000)")
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(["sh", str(root / "scripts/build-chatgpt.sh"), tmp], capture_output=True, text=True)
        if r.returncode:
            errs.append(f"chatgpt build failed: {r.stderr.strip()}")
        else:
            for name in ("instructions.md", "knowledge.md"):
                cur = root / "chatgpt" / name
                if not cur.exists() or cur.read_bytes() != (Path(tmp) / name).read_bytes():
                    errs.append(f"{cur}: chatgpt/{name} is stale, run scripts/build-chatgpt.sh")

    # 8: citations
    al = root / "scripts" / "citations-allowlist.txt"
    allowed = {l.split("#")[0].strip().lower() for l in read(al).splitlines()} - {""}
    for md in sorted((root / "skills").rglob("*.md")):
        for c in find_citations(read(md)):
            if c not in allowed:
                errs.append(f"{md}: citation {c!r} not in citations-allowlist.txt")
    return errs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    errs = run_checks(ap.parse_args().root)
    print("\n".join(errs) if errs else "OK")
    sys.exit(1 if errs else 0)
