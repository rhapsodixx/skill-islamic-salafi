#!/usr/bin/env python3
"""Local + CI gate. Usage: python3 scripts/check.py [--root PATH]"""
import argparse, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

SKILL = "islamic-salafi"
GRADER = Path("evals/no-fabricated-citations/graders/criteria.md")
# Source key -> spelling variants. Keys are what the allow-list stores.
SOURCES = {
    "bukhari": r"(?:Al-)?Bukhari",
    "muslim": r"Muslim",
    "abu dawud": r"Abu\s+Da(?:wu|u|woo)d",
    "tirmidhi": r"(?:At-|Al-)?Tirmidh?i",
    "nasa'i": r"(?:An-|Al-)?Nasa['’]?i",
    "ibn majah": r"Ibnu?\s+Majah",
    "ahmad": r"Ahmad",
    "islamqa": r"islamqa(?:\.info)?",
    "lajnah": r"(?:Al-)?Lajnah(?:\s+(?:Al-)?Da['’]?a?imah)?",
}
HADITH = ("bukhari", "muslim", "abu dawud", "tirmidhi", "nasa'i", "ibn majah", "ahmad")
SRC_RE = re.compile(r"\b(?:" + "|".join(SOURCES.values()) + r")\b", re.I)
# Any "no. N" / "nomor N" / ".../answers/N" anywhere is a citation number.
NUM_RE = re.compile(r"(?:\b(?:no\.?|nomor)\s*|answers/)(\d+)", re.I)
# Bare "<collection> N" inside a parenthetical, e.g. "(Bukhari 2697)"; "5/266" is volume/page, not a number.
BARE_RE = re.compile(r"\b(" + "|".join(SOURCES[k] for k in HADITH) + r")\s+(\d+)(?![\d/])", re.I)
PAREN_RE = re.compile(r"\([^()]*\)")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def char_len(text: str) -> int:
    return len(text)


def strip_frontmatter(text: str) -> str:
    text = text.lstrip("﻿").replace("\r\n", "\n")
    m = re.match(r"---\n.*?\n---\n?", text, re.S)
    return text[m.end():] if m else text


def canon(src: str) -> str:
    """Map a source spelling (e.g. 'Abu Daud', 'An-Nasa'i', 'islamqa.info') to its key."""
    for k, v in SOURCES.items():
        if re.fullmatch(v, src.strip(), re.I):
            return k
    return src.strip().lower()


def find_citations(text: str) -> list[str]:
    found = {}  # position -> normalized "<source> <number>"
    for m in NUM_RE.finditer(text):
        line_start = text.rfind("\n", 0, m.start()) + 1
        srcs = list(SRC_RE.finditer(text, max(line_start, m.start() - 80), m.start()))
        found[m.start(1)] = f"{canon(srcs[-1].group(0)) if srcs else 'unknown'} {m.group(1)}"
    for p in PAREN_RE.finditer(text):
        for m in BARE_RE.finditer(text, p.start(), p.end()):
            found.setdefault(m.start(2), f"{canon(m.group(1))} {m.group(2)}")
    return [found[k] for k in sorted(found)]


def entries(lines) -> set[str]:
    """Normalize '<source> <number>' lines (comments and blanks ignored)."""
    out = set()
    for l in lines:
        l = l.split("#")[0].strip().lstrip("-").strip()
        m = re.fullmatch(r"(.+?)\s+(\d+)", l)
        if m:
            out.add(f"{canon(m.group(1))} {m.group(2)}")
    return out

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
    allowed = entries(read(al).splitlines())
    for md in sorted((root / "skills").rglob("*.md")):
        for c in find_citations(read(md)):
            if c not in allowed:
                errs.append(f"{md}: citation {c!r} not in citations-allowlist.txt")

    # 9: eval grader allow-list matches scripts/citations-allowlist.txt
    grader = root / GRADER
    if grader.exists():
        g = entries(l for l in read(grader).splitlines() if l.startswith("- "))
        if g != allowed:
            errs.append(f"{grader} and {al} allow-lists differ: only in grader {sorted(g - allowed)}, "
                        f"only in allow-list {sorted(allowed - g)}")
    return errs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    errs = run_checks(ap.parse_args().root)
    print("\n".join(errs) if errs else "OK")
    sys.exit(1 if errs else 0)
