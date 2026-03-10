# Islamic Salafi Skill — OpenClaw Skill

An [OpenClaw](https://openclaw.ai) skill that provides Islamic knowledge strictly within the **Manhaj Salaf** (Salafi methodology), adhering to the aqeedah and manhaj of **Ahlus Sunnah wal Jama'ah** based on the understanding of the **Salafush Shalih** (the pious predecessors: Sahabah, Tabi'een, and Tabi'ut Tabi'een).

---

## Overview

This skill is designed for use with **[OpenClaw](https://openclaw.ai)** — an open-source personal AI assistant framework. It must be installed manually (it is not listed in the OpenClaw Skills Registry).

Once installed, the skill intercepts Islamic questions and responds using a structured, daleel-based (evidence-based) methodology grounded in:

- The Quran and authentic Sunnah
- Shafi'i madhab as the default fiqh framework (reflecting the Indonesian Muslim majority)
- Recognized Salafi scholarship — Indonesian and international

---

## Features

- **Bilingual** — Responds in Bahasa Indonesia or English based on the user's language
- **Daleel-first** — Every ruling is backed by Quran, hadith (with grading), or ijma' of the Salaf
- **Shafi'i-primary** — Presents the Shafi'i position first, then notes stronger cross-madhab opinions where applicable
- **Scholar-cited** — References recognized Indonesian Ustaz and international Kibar Ulama
- **Bid'ah awareness** — Identifies and gently corrects practices contrary to the Salafi manhaj
- **Scope-bounded** — Politely declines non-Salafi methodologies, partisan political Islam, and unverified fatwas

---

## Trigger Keywords

This skill activates for questions about:

- Aqeedah (creed), tawhid, shirk, bid'ah
- Fiqh (jurisprudence), ibadah (worship), muamalah (transactions)
- Hadith, Quran tafsir, fatawa
- Halal/haram rulings, marriage, family in Islam
- Tazkiyatun nafs (spiritual purification)
- Questions starting with: *"dalam Islam"*, *"menurut Islam"*, *"hukum Islam"*, *"bolehkah dalam Islam"*, *"apakah haram"*, *"apa sunnah"*, *"in Islam"*, *"according to Islam"*, *"is it haram"*, *"is it sunnah"*, *"Islamic ruling on"*, *"what does Islam say about"*

---

## Response Format

Every response follows a structured three-part format:

1. **Daleel (Evidence)** — Quran verse, authentic hadith, or ijma' of the Salaf
2. **Scholar Position** — Specific scholar(s) or institution cited
3. **Practical Application** — Actionable guidance for the questioner

Responses open with *Bismillah* or *Alhamdulillah* and close with *Wallahu a'lam*.

---

## File Structure

```
skill-islamic-salafi/
├── SKILL.md                  # Skill definition and full instruction set
├── README.md                 # This file
├── references/
│   ├── aqeedah.md            # Core creed: tawhid, shirk, bid'ah, iman
│   ├── fiqh-ibadah.md        # Worship: salah, zakat, sawm, hajj, taharah
│   ├── muamalah.md           # Finance: riba, contracts, crypto, stocks, e-commerce
│   └── tazkiyah.md           # Spiritual purification, adhkar, tawbah
└── .gitignore
```

---

## Key Scholar References

### Indonesian Scholars (Ustaz)
- Ustaz Khalid Basalamah — General fiqh, aqeedah, dawah
- Ustaz Firanda Andirja — Aqeedah, fiqh, hadith
- Ustaz Erwandi Tarmizi — *Specialist: muamalah & financial fiqh*
- Ustaz Yazid bin Abdul Qadir Jawas (rahimahullah) — Foundational aqeedah

### International Kibar Ulama
- Shaykh Ibn Baz (rahimahullah) — [binbaz.org.sa](https://binbaz.org.sa)
- Shaykh Ibn Uthaymeen (rahimahullah) — [ibnothaimeen.com](https://ibnothaimeen.com)
- Shaykh Al-Albani (rahimahullah) — Hadith tashih/tadh'if
- Shaykh Salih Al-Fawzan — [alfawzan.net](https://alfawzan.net)

### Fatwa Databases
- [islamqa.info](https://islamqa.info) — Shaykh Munajjid's comprehensive fatwa database
- [alifta.net](https://alifta.net) — Lajnah Da'imah (Saudi official fatwa council)
- [rumaysho.com](https://rumaysho.com) — Indonesian everyday fiqh & hadith
- [muslim.or.id](https://muslim.or.id) — Indonesian aqeedah & fiqh

---

## Scope & Limitations

**In scope:**
- Aqeedah, fiqh, tazkiyah, muamalah, fatawa within Salafi/Ahlus Sunnah methodology

**Out of scope** (responded to with polite clarification):
- Non-Salafi aqeedah methodologies (Ash'ari, Maturidi, Sufi tariqah) — except for educational contrast
- Partisan political Islam or hizbiyyah
- Novel fatwas without traceable Salafi or Shafi'i scholarly basis

---

## Installation (OpenClaw)

This skill is **not** available in the OpenClaw Skills Registry and must be installed manually. Follow the steps below.

### Prerequisites

- [OpenClaw](https://openclaw.ai) installed and configured
- `git` installed

### Step 1 — Clone the repository

Clone this repo into your OpenClaw shared skills directory:

```bash
git clone https://github.com/your-username/skill-islamic-salafi ~/.openclaw/skills/islamic-salafi
```

> Alternatively, if you want the skill scoped to a single workspace only, clone it into `<your-workspace>/skills/islamic-salafi` instead.

### Step 2 — Verify the skill is detected

```bash
openclaw skills list
```

You should see `islamic-salafi` in the list. If not, confirm the folder exists at `~/.openclaw/skills/islamic-salafi/` and that `SKILL.md` is present inside it.

### Step 3 — Enable the skill (if needed)

If the skill does not appear as eligible, explicitly enable it in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "islamic-salafi": {
        "enabled": true
      }
    }
  }
}
```

Then restart OpenClaw for the change to take effect.

### Step 4 — Use the skill

Ask any Islamic question in your OpenClaw chat. The skill activates automatically when it detects Islamic topics. You can also invoke it explicitly:

```text
/islamic-salafi <your question>
```

### Keeping the skill up to date

```bash
cd ~/.openclaw/skills/islamic-salafi && git pull
```

---

*Barakallahu fiikum. May Allah grant us correct knowledge and the ability to act upon it.*
