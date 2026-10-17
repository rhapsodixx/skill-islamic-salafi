# Multi-Platform Skill + Adab Persona Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the islamic-salafi skill into one Agent Skills–standard source that installs on Claude Code, Codex, OpenClaw, Hermes and ChatGPT, with CI checks, contributor docs, corrected citations, a rewritten prompt, and a copy-paste adab persona.

**Architecture:** The skill folder `skills/islamic-salafi/` is the single source. Thin wrappers: `.claude-plugin/` JSON for Claude Code, a generated `chatgpt/` bundle for ChatGPT Projects, README instructions for everything else. One stdlib-Python check script (`scripts/check.py`) is the gate run locally and in CI; LLM review and evals run only on same-repo branches.

**Tech Stack:** Markdown, POSIX sh, Python 3 stdlib, `skills-ref` (PyPI), Claude Code CLI (`claude plugin validate`, `claude plugin eval`), GitHub Actions, `anthropics/claude-code-action@v1`.

**Spec:** `docs/superpowers/specs/2026-10-17-multi-platform-skill-design.md`

## Global Constraints

- Skill `name: islamic-salafi`; must equal its folder name.
- `description` ≤ 1,024 characters, third person, keeps the Indonesian and English trigger phrases.
- `SKILL.md` body (frontmatter stripped) ≤ 8,000 characters and ≤ 500 lines.
- `chatgpt/instructions.md` ≤ 8,000 characters; `chatgpt/` is generated and committed, never hand-edited.
- `persona/islamic-adab.md` ≤ 1,500 characters including the markers `<!-- islamic-adab:start -->` and `<!-- islamic-adab:end -->`. Counted in Unicode characters, not bytes.
- No religious ruling, scholar position, or madhab methodology changes. Citation fixes only as listed in the spec's "Citation verification" table.
- MUST/NEVER only for true invariants (no novel fatwas; grade every cited hadith; stay within scope), each with a one-line reason. Sentence-case headings, no ALL CAPS.
- No `version` in `plugin.json`. Plugin and marketplace names must not start with `claude-`/`anthropic-`.
- Repo path for every URL/command: `rhapsodixx/skill-islamic-salafi`. Raw persona URL: `https://raw.githubusercontent.com/rhapsodixx/skill-islamic-salafi/main/persona/islamic-adab.md`.
- License: `LICENSE` = MIT (scripts, CI); `LICENSE-CONTENT` = CC BY-SA 4.0 (`skills/**`, `chatgpt/**`, `persona/*.md`, docs).
- Review and eval workflows never run on fork PRs and never use `pull_request_target`.
- Scripts depend only on what ships on macOS/Linux runners plus `skills-ref` and the `claude` CLI. No `jq`, no PyYAML.

## Review Focus

1. **Contributor files with CRLF line endings or a BOM** — frontmatter detection and char counts must still work; a Windows contributor's PR shouldn't fail for invisible reasons. → test in Task 3.
2. **Folded YAML description (`description: >`)** — length must be measured on the parsed value, not the raw lines. Use `skills-ref read-properties`, not a hand-rolled parser. → test in Task 3.
3. **Non-ASCII persona text (ﷺ, Arabic)** — 1,500 is a character limit; byte counting would wrongly fail a valid file. → test in Task 3.
4. **Build output differing between macOS and Linux** (file order, trailing newlines) — the CI freshness check must not flap. Sort with `LC_ALL=C`. → test in Task 2.
5. **Fork PRs** — review/eval jobs must be *skipped* (green/neutral), not fail for a missing secret. → verified in Task 7.

---

### Task 1: Restructure into plugin layout, licenses, citation fixes

**Files:**
- Move: `SKILL.md` → `skills/islamic-salafi/SKILL.md`; `references/*.md` → `skills/islamic-salafi/references/`
- Create: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `LICENSE`, `LICENSE-CONTENT`
- Modify: `skills/islamic-salafi/references/fiqh-ibadah.md:39`, `skills/islamic-salafi/references/muamalah.md:18,48-52`, `skills/islamic-salafi/SKILL.md` (example blocks lines ~206-247)

**Interfaces:**
- Produces: skill at `skills/islamic-salafi/`; plugin name `islamic-salafi`; marketplace name `islamic-salafi-skills`.

- [ ] **Step 1: Move files with history**

```bash
mkdir -p skills/islamic-salafi && git mv SKILL.md references skills/islamic-salafi/
```

- [ ] **Step 2: Write manifests**

`plugin.json`: `name: "islamic-salafi"`, `description`, `author: {name: "panji gautama"}`, `license: "CC-BY-SA-4.0 AND MIT"`, `homepage`/`repository` = `https://github.com/rhapsodixx/skill-islamic-salafi`. No `version`.
`marketplace.json`: `name: "islamic-salafi-skills"`, `owner: {name: "panji gautama"}`, `plugins: [{name: "islamic-salafi", source: ".", description}]`.

- [ ] **Step 3: Add `LICENSE` (MIT, 2026, panji gautama) and `LICENSE-CONTENT` (CC BY-SA 4.0 legal code, fetched verbatim from creativecommons.org).**

- [ ] **Step 4: Apply citation fixes** exactly per the spec's "Citation verification" table:
  - `fiqh-ibadah.md:39`: `(Al-Albani; islamqa.info fatwa no. 2178)` → Al-Albani position cited via `HR. Abu Dawud no. 179 — graded sahih by Al-Albani`; islamqa 2178 attributed to the Lajnah Da'imah (Fataawa al-Lajnah al-Daa'imah 5/266), "with or without desire".
  - `muamalah.md:18`: remove `Lajnah Da'imah no. 4011`; replace `islamqa.info fatwa no. 22905` with `islamqa.info fatwa no. 13973` for the installment claim.
  - `muamalah.md:52`: replace `258320` with `islamqa.info fatwa no. 360668` plus `<!-- TODO(maintainer): verify 360668 and 504160; confirm gharar/maysir wording -->`.
  - `SKILL.md` examples: Abu Dawud 179 `hasan` → `sahih` (EN `graded sahih by Al-Albani`, ID `disahihkan Al-Albani`); same 2178 re-attribution.
  - Add `<!-- TODO(maintainer): verify -->` next to every scholar "Active" status.

- [ ] **Step 5: Verify**

```bash
pip install skills-ref
skills-ref validate skills/islamic-salafi          # Expected: exit 0
claude plugin validate . --strict                  # Expected: exit 0
grep -rnE "4011|22905|258320|hasan by Al-Albani|dihasankan" skills/   # Expected: no output
```

- [ ] **Step 6: Commit** — `refactor: move skill to plugin layout, add licenses, fix verified citations`

---

### Task 2: ChatGPT bundle build script

**Files:**
- Create: `scripts/build-chatgpt.sh`, `chatgpt/instructions.md`, `chatgpt/knowledge.md` (generated)

**Interfaces:**
- Consumes: `skills/islamic-salafi/SKILL.md`, `skills/islamic-salafi/references/*.md`
- Produces: `scripts/build-chatgpt.sh [OUT_DIR]` (default `chatgpt`), exit 0; deterministic output.

- [ ] **Step 1: Implement** `build-chatgpt.sh` (POSIX sh, `set -eu`):
  - `instructions.md` = SKILL.md with the leading `---…---` frontmatter removed (awk), followed by a blank line and exactly: `Reference material (aqeedah, fiqh, muamalah, tazkiyah, sources, examples) is in the uploaded file knowledge.md. Where these instructions say "read references/<file>.md", look up the section with that file name in knowledge.md.`
  - `knowledge.md` = for each `references/*.md` in `LC_ALL=C` sorted order: `# references/<name>.md`, blank line, file contents, blank line.
  - Strip `\r`. Exactly one trailing newline per output file.

- [ ] **Step 2: Determinism test**

```bash
scripts/build-chatgpt.sh /tmp/a && scripts/build-chatgpt.sh /tmp/b && diff -r /tmp/a /tmp/b   # Expected: no output
head -3 /tmp/a/instructions.md | grep -c '^name:'                                            # Expected: 0
grep -c '^# references/' /tmp/a/knowledge.md                                                  # Expected: 4 (6 after Task 4)
```

- [ ] **Step 3: Generate and commit** — `scripts/build-chatgpt.sh && git add scripts chatgpt && git commit -m "feat: add ChatGPT Project bundle build"`. (`instructions.md` will be over 8,000 chars until Task 4; that's expected.)

---

### Task 3: Check script (the local + CI gate)

**Files:**
- Create: `scripts/check.py`, `scripts/citations-allowlist.txt`, `scripts/test_check.py`

**Interfaces:**
- Consumes: `scripts/build-chatgpt.sh OUT_DIR`; `skills-ref read-properties <dir>` (JSON with `name`, `description`).
- Produces: `python3 scripts/check.py [--root PATH]` → prints one line per failure, exit 1 if any, else `OK` and exit 0. Functions (importable for tests): `char_len(text: str) -> int`, `strip_frontmatter(text: str) -> str`, `find_citations(text: str) -> list[str]`, `run_checks(root: Path) -> list[str]`.

Checks performed by `run_checks`, each producing a message naming the file:
1. `name` (via `skills-ref read-properties`) == folder name `islamic-salafi`.
2. `description` ≤ 1,024 chars.
3. SKILL.md body ≤ 8,000 chars and ≤ 500 lines.
4. Every `references/<file>.md` mentioned in SKILL.md exists.
5. `.claude-plugin/*.json` parse with `json.load`.
6. `persona/islamic-adab.md` (if present) ≤ 1,500 chars and contains both markers.
7. `chatgpt/instructions.md` ≤ 8,000 chars; rebuilding into a temp dir gives byte-identical `chatgpt/`.
8. Every citation found by `find_citations` in `skills/**/*.md` appears in `citations-allowlist.txt`.

`find_citations` returns normalized `"<source> <number>"` strings for: `islamqa.info fatwa no. N`, `HR. <Collection> no. N` (Bukhari, Muslim, Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah, Ahmad), case-insensitive, tolerating `no.N`, `no N`, `nomor N`. Collections joined by comma share the `HR.` prefix (`HR. Bukhari no. 2697, Muslim no. 1718` → both).

`citations-allowlist.txt` (one per line, `#` comments allowed), seeded from the spec table:
```
islamqa 1027
islamqa 2178
islamqa 13973
islamqa 22905
islamqa 360668   # TODO(maintainer): verify
bukhari 2697
muslim 1718
abu dawud 179
muslim 399
muslim 360
muslim 91
muslim 597
muslim 1163
```

- [ ] **Step 1: Write failing tests** in `scripts/test_check.py` (plain `assert`, runnable with `python3 scripts/test_check.py`):

```python
assert char_len("ﷺ" * 1500) == 1500
assert strip_frontmatter("---\r\nname: x\r\n---\r\nbody\r\n").strip() == "body"
assert strip_frontmatter("﻿---\nname: x\n---\nbody").strip() == "body"
assert find_citations("(HR. Bukhari no. 2697, Muslim no. 1718)") == ["bukhari 2697", "muslim 1718"]
assert find_citations("islamqa.info fatwa no.258320") == ["islamqa 258320"]
assert find_citations("HR. Muslim nomor 91") == ["muslim 91"]
assert find_citations("Lajnah Da'imah 5/266") == []
# run_checks on a temp copy of the repo:
#   unchanged repo after Task 4 -> []
#   persona with 1,501 ASCII chars -> one message containing "islamic-adab.md"
#   SKILL.md with "islamqa.info fatwa no. 99999" added -> one message containing "99999"
#   hand-edited chatgpt/knowledge.md -> one message containing "chatgpt"
```

- [ ] **Step 2: Run** `python3 scripts/test_check.py` — Expected: fails (ImportError).

- [ ] **Step 3: Implement `scripts/check.py`.** Decode files with `encoding="utf-8-sig"`, normalize `\r\n` → `\n` before any count.

- [ ] **Step 4: Run** `python3 scripts/test_check.py` — Expected: unit asserts pass. `python3 scripts/check.py` — Expected: exit 1, only failures are SKILL.md body size and `chatgpt/instructions.md` size (fixed in Task 4).

- [ ] **Step 5: Commit** — `feat: add check script with citation allow-list`

---

### Task 4: Rewrite SKILL.md for Claude + GPT-5.x

**Files:**
- Modify: `skills/islamic-salafi/SKILL.md`
- Create: `skills/islamic-salafi/references/sources.md`, `skills/islamic-salafi/references/examples.md`
- Regenerate: `chatgpt/`

**Interfaces:**
- Consumes: Task 3 `check.py`.
- Produces: final skill content; `references/` now has 6 files.

- [ ] **Step 1: Move content out** (verbatim, plus TODO marks only):
  - `sources.md`: the Shafi'i classical texts table, qawl jadid note, Indonesian sources table, Indonesian ustaz list, Kibar Ulama table, international websites. Add at top: `Hadith numbers for Sahih Muslim use Fu'ad Abdul Baqi numbering.`
  - `examples.md`: the three worked examples (after Task 1's fixes), each fenced in `<example>` tags and reshaped to the single response shape below, with an opening line `These are illustrative; match the shape, not the wording.`

- [ ] **Step 2: Rewrite SKILL.md body** applying spec rules 1-7. Required elements:
  - Description: third person, what + when, keeps the trigger phrases `dalam Islam`, `menurut Islam`, `hukum Islam`, `bolehkah dalam Islam`, `apakah haram`, `apa sunnah`, plus English `in Islam`, `is it haram`, `Islamic ruling on`.
  - One response shape: **Daleel** → **Positions** (Shafi'i mu'tamad first; stronger daleel position if it differs, labeled) → **Practical guidance**; opens with Bismillah, closes with Wallahu a'lam.
  - Citation rule (verbatim intent): cite fatwa/hadith numbers or URLs only when they appear in the reference files; otherwise name the scholar and work, or use the uncertainty protocol.
  - The three invariants in MUST form, each with a one-line reason; all else plain imperative.
  - Scope line rewritten to: out of scope are fiqh opinions that neither the Shafi'i madhab nor recognized Salafi scholarship supports.
  - "Read when" links: `references/aqeedah.md`, `fiqh-ibadah.md`, `muamalah.md`, `tazkiyah.md`, `sources.md` (read when citing a scholar or site), `examples.md` (read before the first answer in a session).

- [ ] **Step 3: Verify**

```bash
scripts/build-chatgpt.sh
python3 scripts/check.py                                     # Expected: OK, exit 0
python3 scripts/test_check.py                                # Expected: all pass (incl. run_checks cases)
grep -nE '^#+ [A-Z &]{6,}$' skills/islamic-salafi/SKILL.md   # Expected: no ALL-CAPS headings
grep -c 'MUST' skills/islamic-salafi/SKILL.md                # Expected: ≤ 3
skills-ref validate skills/islamic-salafi && claude plugin validate . --strict   # Expected: exit 0
```

- [ ] **Step 4: Spot check by hand** in Claude Code (`claude --plugin-dir .`): ask one ID and one EN question from `examples.md`; answer follows the shape and cites no number outside the allow-list.

- [ ] **Step 5: Commit** — `feat: rewrite skill prompt for Claude and GPT, split sources and examples`

---

### Task 5: Adab persona

**Files:**
- Create: `persona/islamic-adab.md`

**Interfaces:**
- Consumes: Task 3 check #6.

- [ ] **Step 1: Write the persona** between the two markers, per spec "Adab persona → Content": restraint rule first; Bismillah/Alhamdulillah/In sha Allah/Masha Allah/Wallahu a'lam; honorifics (ﷺ, 'alayhis salam, radhiyallahu 'anhu/'anha, rahimahullah, subhanahu wa ta'ala); salam reply, Jazakallahu khairan, Astaghfirullah, Barakallahu fik; Islamic questions within Ahlus Sunnah wal Jama'ah, pointing to the islamic-salafi skill when installed, with the citation guardrail. Calm voice, no MUST/ALWAYS.

- [ ] **Step 2: Verify** — `python3 scripts/check.py` → `OK`. Paste into a fresh Claude Code session's `CLAUDE.md` (temp `HOME`) and ask (a) "fix this typo in README" → no religious commentary beyond a natural opener; (b) an uncertain fiqh question → ends with Wallahu a'lam, no fatwa numbers.

- [ ] **Step 3: Commit** — `feat: add copy-paste Islamic adab persona`

---

### Task 6: CI format gate

**Files:**
- Create: `.github/workflows/ci.yml`, `.markdownlint.json`

- [ ] **Step 1: Write `ci.yml`**: `on: pull_request` + `push: branches: [main]`; `permissions: contents: read`; steps: checkout, setup-python 3.12, `pip install skills-ref`, `npm i -g @anthropic-ai/claude-code`, `skills-ref validate skills/islamic-salafi`, `claude plugin validate . --strict`, `python3 scripts/test_check.py`, `python3 scripts/check.py`, `npx markdownlint-cli2 "**/*.md" "#node_modules"`. No secrets referenced.

- [ ] **Step 2: `.markdownlint.json`**: `{"default": true, "MD013": false, "MD033": false}` (inline HTML needed for markers/TODO comments). Fix any lint errors it reports in repo markdown.

- [ ] **Step 3: Verify locally** — run each command above; all exit 0. Push a branch, open a draft PR; `ci` job green.

- [ ] **Step 4: Commit** — `ci: add format and check gate`

---

### Task 7: LLM review + evals (same-repo only)

**Files:**
- Create: `.github/workflows/review.yml`, `.github/workflows/eval.yml`, `evals/<case>/prompt.md` + `evals/<case>/graders/*.md` (6 cases)

**Interfaces:**
- Consumes: plugin `islamic-salafi@islamic-salafi-skills`; `scripts/citations-allowlist.txt` (graders reference it).

- [ ] **Step 1: `review.yml`**: `on: pull_request` (opened, synchronize, ready_for_review, reopened); job `if: github.event.pull_request.head.repo.full_name == github.repository`; permissions `contents: read, pull-requests: write, id-token: write`; `anthropics/claude-code-action@v1` with `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}` and a `prompt` that reviews changed files under `skills/` and `persona/` against spec "Prompt rewrite rules" 1-7 and the Global Constraints (fabrication pressure, emphasis, contradictions, cross-model wording, size), explicitly not judging religious correctness, posting inline comments.

- [ ] **Step 2: Scaffold evals** with `claude plugin eval init --bare <case>` for: `no-fabricated-citations`, `replies-in-indonesian`, `replies-in-english`, `shafii-first-layered`, `ends-wallahu-alam`, `declines-hizbiyyah`, `uncertainty-protocol`. Graders state pass/fail criteria; `no-fabricated-citations` grader fails any fatwa/hadith number not in `citations-allowlist.txt` (contents inlined into the grader by the builder).

- [ ] **Step 3: `eval.yml`**: `on: pull_request` (same fork `if:`) + `push: branches: [main]`; runs `claude plugin eval . --trust-plugin --json results.json --threshold 0.8 --model <pinned> --judge-model <pinned> --no-publish --max-cost-usd 5`; uploads `results.json` as an artifact.

- [ ] **Step 4: Verify**
  - Local: `claude plugin eval . --trust-plugin --threshold 0.8 --max-cost-usd 5` — Expected: exit 0.
  - Same-repo draft PR: `review` posts a comment; `eval` passes.
  - Fork PR (from a test fork): `review` and `eval` show **skipped**, `ci` runs and passes.

- [ ] **Step 5: Commit** — `ci: add same-repo LLM review and skill evals`

---

### Task 8: README, CONTRIBUTING, PR template

**Files:**
- Modify: `README.md`
- Create: `CONTRIBUTING.md`, `.github/pull_request_template.md`

- [ ] **Step 1: README** — sections: what it is; Install (Claude Code, Codex, OpenClaw, Hermes, ChatGPT Business/Enterprise/Edu, ChatGPT Free/Plus Project) with commands from the spec tables, each re-verified against current docs at write time; Persona (table + one-liners + update/remove notes from spec); File structure; License split; Contributing link. Drop "OpenClaw-only" framing.

- [ ] **Step 2: CONTRIBUTING.md** — how to edit (skill text vs references vs persona), never edit `chatgpt/` by hand (run `scripts/build-chatgpt.sh`), run `pip install skills-ref && python3 scripts/check.py` locally, new citation numbers must be added to `scripts/citations-allowlist.txt` with a source link in the PR, maintainer reviews religious content by hand, fork PRs don't get AI review automatically.

- [ ] **Step 3: PR template** — checklist: source link/book for every new or changed ruling or citation; allow-list updated; `check.py` passes; no ruling changes hidden in wording edits.

- [ ] **Step 4: Verify** — `python3 scripts/check.py` OK; markdownlint clean; every install command in README was copied from a doc page checked today (list URLs in the PR description).

- [ ] **Step 5: Commit** — `docs: multi-platform install, persona, contributing guide`
