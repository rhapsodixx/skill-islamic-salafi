"""Run: python3 scripts/test_check.py"""
import shutil, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check import char_len, strip_frontmatter, find_citations, run_checks

ROOT = Path(__file__).resolve().parent.parent

assert char_len("ﷺ" * 1500) == 1500
assert strip_frontmatter("---\r\nname: x\r\n---\r\nbody\r\n").strip() == "body"
assert strip_frontmatter("﻿---\nname: x\n---\nbody").strip() == "body"
assert find_citations("(HR. Bukhari no. 2697, Muslim no. 1718)") == ["bukhari 2697", "muslim 1718"]
assert find_citations("islamqa.info fatwa no.258320") == ["islamqa 258320"]
assert find_citations("HR. Muslim nomor 91") == ["muslim 91"]
assert find_citations("Lajnah Da'imah 5/266") == []


def temp_repo():
    d = Path(tempfile.mkdtemp())
    shutil.copytree(ROOT, d / "r", ignore=shutil.ignore_patterns(".git", ".venv", ".superpowers"))
    return d / "r"


r = temp_repo()
assert run_checks(r) == [], run_checks(r)

skill = r / "skills/islamic-salafi/SKILL.md"
orig = skill.read_text(encoding="utf-8")
skill.write_bytes(orig.replace("\n", "\r\n").encode())
assert run_checks(r) == [], run_checks(r)
# BOM: our own checks and the ChatGPT build tolerate it; the agentskills validator rejects it (correctly).
skill.write_bytes("\ufeff".encode() + orig.replace("\n", "\r\n").encode())
f = run_checks(r)
assert len(f) == 1 and "must start with YAML frontmatter" in f[0], f
skill.write_text(orig, encoding="utf-8")

p = r / "persona"
p.mkdir(exist_ok=True)
start, end = "<!-- islamic-adab:start -->\n", "\n<!-- islamic-adab:end -->\n"
fill = "ﷺ بسم الله "
pad = 1500 - len(start) - len(end)
adab = start + (fill * pad)[:pad] + end
assert len(adab) == 1500
(p / "islamic-adab.md").write_text(adab, encoding="utf-8")
assert run_checks(r) == [], run_checks(r)
(p / "islamic-adab.md").write_text(adab.replace(end, "ﷺ" + end), encoding="utf-8")
f = run_checks(r)
assert len(f) == 1 and "islamic-adab.md" in f[0], f
shutil.rmtree(p)

skill.write_text(orig + "\nislamqa.info fatwa no. 99999\n")
f = [m for m in run_checks(r) if "99999" in m]
assert len(f) == 1, f
skill.write_text(orig)

with open(r / "chatgpt/knowledge.md", "a") as fh:
    fh.write("hand edit\n")
f = [m for m in run_checks(r) if "chatgpt" in m and "instructions.md" not in m]
assert len(f) == 1, f
shutil.rmtree(r.parent)
print("test_check: OK")
