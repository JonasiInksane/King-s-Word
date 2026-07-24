# 王の言霊 — The King's Word

A modern-Japan webnovel: neon cities, a creeping war, ordinary teenagers at the edge of something enormous.

## Logline

Three high-school friends in Kōgetsu City live an ordinary life — until two of the boys discover they carry the **Ō no Kotodama (王の言霊)**, the King's Word: a near-extinct power that forces anyone who *hears and understands* a command to obey it. On the night of the girl's sixteenth birthday, the war reaches home. What follows fractures a friendship, one careless sentence at a time.

## Core tragedy (prologue)

Kaito screams **"Let her go"** at a soldier holding Ryn over a ledge as leverage. The Word obeys the grammar. She falls. Guilt, Backwash, and Mira's reframing begin to pull him from Haruki. Soft fork on the tide flats: Haruki can release; Kaito cannot.

## POV

**Canon lives in this section only** — do not restate POV locks in lore files.

- **Mains:** Haruki and Kaito. Most of the story runs through them.
- **Prologue frame:** Kitchen **present** with **Sugi** (not *you*). Past recount starts at *It started…* and runs to her door. Then **present live** again — telling over.
- **Guests:** Other first-person cameras when they add depth the boys cannot see. Not padding.
- **Per chapter:** One POV is default, not a lock. Multiple POVs in one chapter are allowed when a cut earns it — keep switches clean (scene break + clear camera), never muddy.
- **Do not drift Haruki-only** after the hard split. Kaito (and guests) stay in rotation when their side of the fork matters.
- **All volumes:** Same rules. No fixed alternate-chapter schedule.
- **Length:** Floor **1,000 words**; longer chapters are fine when the beat earns them (see `.cursor/rules/story-writing.mdc`).

## Style guide

Aim for the propulsion of `assets/example-chapter-1`: **story in clear sentences**, not essay, not haiku.

- **Open in motion.** First lines = something happening. Skip city-thesis openers and portrait inventories.
- **Tell the story.** Cause → action → result. Explain enough to follow. If a line is only mood, cut it or attach it to a task.
- **Attach description to task.** Looks, room, city detail land while hands and eyes are busy. Spatial clarity when action matters.
- **Complication rhythm.** Scenes push on a problem, not banter alone.
- **Deep POV.** Feel the world through the camera's body and diction — plain, not poetic. Guests get their own voice.
- **Show, don't brief.** Lore leaks through dialogue, signage, apps, what people do under pressure.
- **Camera moment.** New people arrive in a vivid beat, not a bio dump.
- **Close on a pull.** End mid-motion, on a spoken line, or on a concrete next step — not sleep/bed twice in a row, not ornamental metaphor, not a one-line haiku button.
- **Dialogue and narration stay plain.** Normal sentences. Clear and concrete. **No poetry-in-every-clause. No travel montages made of fragments.** See `.cursor/rules/story-writing.mdc`.
- **No inventory talk (hard).** No telegram stub-chains ("Further in. Girl with him." / "Midnight. All three.") in dialogue or narration.
- **No "soft" bulletin speech (hard).** Do not write mission jargon like "ask soft" / "I say no. Soft." Say it in ordinary sentences. See `.cursor/rules/story-writing.mdc`.
- **No "written down" spam (hard).** Do not default every caution to *get written down* / *worth the ink*. Show FDC risk; don't catchphrase it. See `.cursor/rules/story-writing.mdc`.
- **No trail-formula spam (hard).** Do not reuse *tall boy / scraped voice / girl did the asking* on every ask. Vary. See `.cursor/rules/story-writing.mdc`.
- **No thin recap stacks / no pre-break buttons (hard).** Do not end a beat/scene by restating what just happened, and do not park a neat narrator wrap right before `---`. End on talk or the next move. See `.cursor/rules/story-writing.mdc`.
- **Conversations must engage (hard).** Not one-line teleports. People push back, ask wrong questions, refuse partway. See `.cursor/rules/story-writing.mdc`.
- **Lean dialogue pass (hard).** Cut extra clauses; NPCs in full sentences; plain closes (no title-echo buttons); less narrator garnish on talk. User dialogue rewrites = canon voice for following chapters. See `.cursor/rules/story-writing.mdc`.
- **Chapter length (hard).** Finished live chapters: **1,000-word floor**, target **1,100–1,400**. Check count before calling a chapter done; expand with real scene, not poetry padding. See `.cursor/rules/story-writing.mdc`.
- **Naming:** Japanese order Surname Given. Prose uses first names for the trio.
- **Spelling:** **gray-green** in prose.
- **Prologue restraint:** no Word-naming to the boys, no sentence-craft lesson, no Literal→Intent teaching. Soft fork only.

### Hard rules (AI + drafting)

Full always-on rule: `.cursor/rules/story-writing.mdc`.

- **No writer-only leaks.** Forks, stages, outline jargon, magic-system labels, continuity notes — never in dialogue or thoughts unless that character has earned them on-page.
- **Knowledge hygiene.** People only speak what they know. New characters don't bleed secrets only old characters have. POV is not omniscient; rumors stay rumors.
- **Smooth progression, no repetition.** Advance want/cost/relationship; don't re-teach the same beat every chapter.
- **No inventory talk (hard).** Full sentences only — not stub-chains. See `.cursor/rules/story-writing.mdc`.
- When unsure: silence or wrong guesses beat convenient exposition.

## Project structure

```
README.md                 <- you are here (POV + style live here)
PROGRESS.md               <- living continuity (rewrite from scratch)
lore/
  world.md                <- places, geography, daily texture
  magic-kings-word.md     <- Word rules + Rewrite
  factions.md             <- nations / orders / war
  characters.md           <- bios, voices, secrets (not POV schedule)
  plot-outline.md         <- arc spine; post-prologue rebuilds here
chapters/                 <- live blank-page drafts only
archive/
  pre-rewrite/            <- older mine
  clean-slate-2026-07-23/ <- last live pass (Ch 1–50 + PROGRESS + meetings)
assets/example-chapter-1  <- craft reference
export/                   <- PDFs
scripts/export_pdf.py
```

Archived prose is a **mine for texture**, not continuity law. Bible + live outline win.

## Export

```bash
pip install -r scripts/requirements-pdf.txt
python scripts/export_pdf.py
python scripts/export_pdf.py --combined
```

## How to resume

1. `PROGRESS.md`
2. `lore/plot-outline.md` (prologue locked; rest TBD)
3. Write the next chapter in `chapters/` from a blank page
4. Update PROGRESS after each chapter (meetings go there or a new meeting log when you need one)
