# Translations

Language-by-language translations of the text produced from the rails. Each subfolder is one **translation track** — one (target-language × style × audience) combination — and contains the two governing files plus the generated output:

```
Translations/
└── <lang>-<track-name>/
    ├── requirements.md # the style contract (in the target language)
    ├── termbase.md     # the vocabulary contract (one chosen rendering per keyword)
    ├── audience.md     # the audience profile
    ├── <output>.md     # the translation file(s), one per source-text section
    └── qa-report.md   # MQM-taxonomy critique driving the next revision
```

For the category-wide convention (what `requirements.md` and `termbase.md` must contain, the citation chain, the status lifecycle, the checklists), see [`../About Transformations.md`](../About Transformations.md). This README focuses on the **per-track workflow** — the three-phase pipeline that turns rails into a reviewed translation.

---

## Current tracks

No tracks exist yet — add them as they are commissioned. Each track folder is named `<lang>-<descriptor>/` (e.g. `en-contemporary/`, `bn-scholarly/`). Each track's `requirements.md` is written **in its own target language** — the working language for that track's drafters and reviewers.

---

## The translation pipeline — three phases, three failure modes

Producing a reliable AI-assisted translation requires three sequential phases. Each phase exists to defuse one of the three core failure modes of AI translation.

| Failure mode | Where it is addressed |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hallucinations — fabricated meaning at section or verse level | Phase 1 (context preparation) → `2-RAILS/Sections/`, `2-RAILS/Verses/`, `2-RAILS/Local-Wiki/` |
| Inconsistent vocabulary — the same source term rendered differently | Phase 1 (context preparation) → `2-RAILS/Bilingual-Glossaries/` and the per-track `termbase.md` |
| Inconsistent style over long texts | `requirements.md` for the track (binding style contract) + Phase 3 QA using the MQM taxonomy |

### Phase 1 — Context preparation

Runs entirely in `2-RAILS/`. See [`../../2-RAILS/About Rails.md`](../../2-RAILS/About Rails.md) for the rules. The four sub-steps:

- **1a. Section-level context (`2-RAILS/Sections/`).** For every node in the table of contents, generate per-commentary raw summaries in the original language, then combine them with an English translation underneath. These combined files orient the translation skill before each section.
- **1b. Verse-level context (`2-RAILS/Verses/`).** For each verse, produce a context file that transcludes the relevant commentary passages, synthesises the commentators' interpretations in the original language, and produces a **disambiguated restatement** of the verse — precise enough to exclude any mistranslation. The translation skill works from this restatement, not the raw verse.
- **1c. Word-level context (`2-RAILS/Local-Wiki/`).** For each key term, an article with verbatim commentary quotations and a contextual definition — the reference of last resort when a bilingual glossary entry does not yet capture a term adequately.
- **1d. Bilingual Glossary chain (`2-RAILS/Bilingual-Glossaries/`).** Interlinear glosses per existing translation → raw per-translation bilingual glossaries → consolidated per-language-pair bilingual glossary → **per-track termbase** in this folder (Phase 1 of *this* track).

The translation skill cannot run until the rails for the batch it covers are at `status: complete`.

### Phase 2 — Translation

Work in small batches through the table of contents — one or a few TOC nodes at a time, never the whole text at once:

1. **Select** a small batch of nodes.
2. **Fetch the per-track termbase** from `Translations/<track>/termbase.md`.
3. **Fetch context at every relevant level from `2-RAILS/`**: the combined section summary for each node, the verse-context file for every verse, and any Local-Wiki articles for terms not covered by the termbase.
4. **Translate and write** the result into `Translations/<track>/`. The translation file's frontmatter lists the rails it was generated from.

The translation skill works from the **disambiguated restatement** in each verse-context file, not from the raw root text. The disambiguated restatement is precise enough that no misreading is possible — the translation is then target-language work only.

Hard rules: never translate a batch without first loading all three levels of context; never introduce a keyword rendering that is not in the per-track termbase without recording the new rendering in the termbase first and feeding it back into the consolidated bilingual glossary under `2-RAILS/Bilingual-Glossaries/`.

### Phase 3 — QA

Review each translated section against the **MQM (Multidimensional Quality Metrics) error taxonomy**, comparing the translation back to `requirements.md` and — wherever an accuracy or terminology question arises — to the corresponding `2-RAILS/Sections/`, `2-RAILS/Verses/`, and `2-RAILS/Local-Wiki/` files. For each issue found, record:

- the segment (verse ID or paragraph anchor),
- the MQM error category (accuracy, fluency, terminology, style, locale convention, …),
- severity (critical / major / minor),
- and a suggested correction.

All findings go into `Translations/<track>/qa-report.md`. That report drives the next revision pass. A section is not considered `complete` until it has passed QA with no critical or major errors outstanding.

In addition to per-section QA, the `style-consistency-check` skill *(planned)* scans across many already-translated sections of one track to catch style drift over long texts — the failure mode that section-by-section QA tends to miss. Its findings append to `qa-report.md` as a style-drift section.

---

## File-level rules

- Translation files name their language with the tag (`en`, `bo`, `zh`, `pi`, `hi`, …) per the vault's convention (see [`../../1-SOURCES/About Sources.md`](../../1-SOURCES/About Sources.md) §Language tags).
- Each translation file's frontmatter cites the rails it was generated from. The citation chain (`1-SOURCES/` → `2-RAILS/` → `3-TRANSFORMATIONS/`) never skips.
- Only `status: complete` translation files are referenced by other transformations (e.g. published into a plan day-file).
