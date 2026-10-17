# Contributing

## What to edit

- Skill behaviour: `skills/islamic-salafi/SKILL.md`. Keep the body under 8,000 characters (the ChatGPT bundle depends on it).
- Reference material: `skills/islamic-salafi/references/*.md`.
- Persona: `persona/islamic-adab.md`. Keep the start and end marker comments.
- Never edit `chatgpt/` by hand. After changing the skill, run `scripts/build-chatgpt.sh` and commit the output. CI rebuilds it and fails on any difference.

## Run checks locally

```bash
python3 -m venv .venv && .venv/bin/pip install skills-ref && python3 scripts/check.py
npx --yes markdownlint-cli2
```

`check.py` finds `.venv/bin/agentskills` automatically and prints `OK` on success.

## Citations and sources

- Every new or changed ruling or citation needs a source link or book reference in the PR.
- New citation numbers must be added to `scripts/citations-allowlist.txt`, with the source link in the PR.
- The maintainer reviews religious content by hand. Do not hide ruling changes inside wording edits.

## CI and cost

- Every PR runs the format and check gate.
- The AI review and evals run only for branches inside this repository. Fork PRs get the format gate only; the maintainer may run the rest manually.
- A full eval run costs about $2.65 in API usage, so keep eval pushes deliberate.
