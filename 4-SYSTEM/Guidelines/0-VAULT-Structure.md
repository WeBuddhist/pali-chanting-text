# 0-VAULT — Vault File Structure

This document describes the top-level architecture of a 🛤️ Railroads vault. It is the orientation guideline — read it first, then continue to [`../../1-SOURCES/About Sources.md`](../../1-SOURCES/About Sources.md) for source-file rules, [`../../2-RAILS/About Rails.md`](../../2-RAILS/About Rails.md) for the rails schema, and [`../../3-TRANSFORMATIONS/About Transformations.md`](../../3-TRANSFORMATIONS/About Transformations.md) for the transformation rules.

This guideline is **text-agnostic**. The structure below applies to any Railroads vault — Bodhicaryāvatāra, Mūlamadhyamakakārikā, Abhidharmakośa, the Pāli Nikāyas, or any other classical text the methodology is applied to. Examples here use placeholders (`[text-slug]`, `[lang]`, `[commentary-name]`); the per-vault specifics are filled in by the text it serves.

---

## 1. One Vault Per Text

A Railroads vault holds the complete interpretive ecosystem for **one classical text**: its editions, translations, commentaries, sub-commentaries, secondary literature, the compiled rails, and any generated outputs.

This is a deliberate constraint. Mixing texts in a single vault would mean:

- Block ID collisions across texts (e.g. `^1-1` of one text vs. another)
- Commentary attributions that have to disambiguate by text every time they are cited
- Local-wiki sense IDs that vary across texts being conflated
- Bilingual Glossaries that lose their per-text descriptive grounding

Each vault is named for the text it serves — typically `[text-slug]-rails` (e.g. `bodhisattvacharyavatara-rails`, `mulamadhyamakakarika-rails`). The vault is portable: cloning or copying it transfers the complete interpretive context for that text in one move.

**What goes in the vault:** anything that is *about* this text — its editions, translations, commentaries on it, secondary literature on it, bilingual glossaries derived from its translation tradition, rails compiled from its commentary tradition, transformations generated from those rails.

**What does not go in the vault:** general reference works (Sanskrit grammars, Tibetan dictionaries, Buddhist encyclopedias) unless they have entries specifically on this text. General reference belongs in a separate reference vault and is linked to externally.

---

## 2. Top-Level Folder Structure

```
[text-slug]-rails/
├── 0-INBOX/              # drafts, scratch, raw downloads — not authoritative
├── 1-SOURCES/            # human-produced material — read-only ground truth
│   ├── Text/             # root text(s) and editions
│   ├── Commentaries/     # authored commentaries
│   ├── Translations/     # translations into other languages
│   ├── References/       # secondary literature, dictionaries with entries on this text
│   └── Audio/            # recitation and teaching recordings
├── 2-RAILS/              # compiled interpretive context (the rails)
│   ├── Verses/           # one package per verse or analytical unit
│   ├── Sections/         # per-chapter summaries and structural outlines
│   ├── Local-Wiki/       # one page per attested sense ID
│   └── Bilingual-Glossaries/       # bilingual term mappings, per language pair
├── 3-TRANSFORMATIONS/    # outputs generated from the rails, in three categories
│   ├── Translations/     # language-by-language translation tracks
│   ├── Adaptations/      # audience-targeted retellings
│   └── Plans/            # calendar-driven study/practice arcs
└── 4-SYSTEM/             # guidelines, skills, templates, agent instructions
    ├── Guidelines/       # cross-cutting methodology docs (this folder)
    ├── Skills/           # repeatable workflows (ingest, format, extract, translate, QA)
    ├── Templates/        # blank file templates for each frontmatter type
    ├── How-to guides/    # human-facing instructions for non-AI tasks
    ├── gemini-scribe/    # Gemini Scribe plugin workspace
    └── CLAUDE.md         # LLM-facing operational instructions
```

The vault root also contains:

- `README.md` — orientation for any contributor (human or AI) visiting the repo. Holds the canonical reading paths.

Top-level folders are numbered to enforce visual reading order: sources come before rails come before transformations. The canonical rules for each of those folders live inside that folder's own `About <FolderName>.md` doc — *not* in this Guidelines folder. The Guidelines folder holds only cross-cutting methodology that doesn't belong to any single layer.

---

## 3. Per-Folder Purpose

### `0-INBOX/`

Scratch space. Anything not yet ready to be placed in its proper folder lives here. Common contents:

- Raw downloads (e.g. EPUB files before conversion)
- `temp/` — files mid-conversion or mid-review
- `raw-data/` — original-format dumps before structural processing
- `md-texts/` — markdown versions of files being prepared for `1-SOURCES/`
- Draft notes, outline sketches, working documents

**Nothing in `0-INBOX/` is authoritative.** Files here are not cited by anything in `2-RAILS/` or `3-TRANSFORMATIONS/`. They move out of inbox as they are formatted and verified.

### `1-SOURCES/`

Human-produced material exactly as received. This is the ground truth — every claim in the rails ultimately cites a passage here. The folder is **append-only and read-only for the LLM**: it adds block IDs, frontmatter, and navigation links, but never interpretive content.

Subfolders:

- `Text/` — the root text in its primary language, plus alternative-script editions (e.g. IAST or Wylie versions of a Devanāgarī or Unicode-Tibetan root). One file per edition.
- `Commentaries/` — authored commentaries on the text. One file per commentary, regardless of length. Block IDs follow the commentary author's own structural system (chapter-verse, folio-line, section-paragraph, etc.) as declared in frontmatter.
- `Translations/` — translations of the root text into other languages. One file per translation. Block IDs correspond to the source verse, not the translator's numbering.
- `References/` — secondary literature with substantive content on this text: monographs, articles, dictionaries with entries specific to the text.
- `Audio/` — recitation and teaching recordings, aligned to source-text block IDs where possible.

Naming conventions, frontmatter requirements, block ID rules, and editorial note conventions are specified in [`../../1-SOURCES/About Sources.md`](../../1-SOURCES/About Sources.md).

### `2-RAILS/`

The rails — compiled interpretive packages that resolve every significant ambiguity in the text, citing the human sources that determine each decision. This is where the LLM does its primary work, under domain-specialist review.

Subfolders:

- `Verses/` — one package per verse or analytical unit. Files named by block ID without the caret (`1-1.md`, `6-33.md`, `0-4.md` for pre-chapter content).
- `Sections/` — per-chapter or per-section summaries synthesised from the verse packages and from structural outlines extracted from each commentary.
- `Local-Wiki/` — one page per attested sense ID within this text. Sense IDs are Wikipedia-style: `term (disambiguating phrase)`, e.g. `bodhicitta (awakening mind)`.
- `Bilingual-Glossaries/` — bilingual lexicons, one file per language pair (`pi-en.md`, `pi-bn.md`, etc.). Derived descriptively from the translations in `1-SOURCES/Translations/`.

Frontmatter, package layout, the disambiguation stack, citation rules, and divergence-flagging conventions are specified in [`../../2-RAILS/About Rails.md`](../../2-RAILS/About Rails.md).

### `3-TRANSFORMATIONS/`

Generated outputs — translations, adaptations, lesson plans, study guides, daily reading content. The folder is organised into **three categories**, each a top-level subfolder; each second-level folder is one **track** governed by `requirements.md` (style contract) + `termbase.md` (vocabulary contract):

```
3-TRANSFORMATIONS/
├── Translations/             # language-by-language translations
│   └── [track-id]/
│       ├── requirements.md   # the style contract
│       ├── termbase.md       # the vocabulary contract
│       ├── audience.md       # the audience profile
│       ├── <output>.md       # the generated translation files
│       └── qa-report.md      # MQM-taxonomy critique driving the next revision
├── Adaptations/              # audience-targeted retellings
│   └── [track-id]/
│       ├── requirements.md
│       ├── audience.md
│       ├── termbase.md
│       └── <output>.md
└── Plans/                    # calendar-driven study/practice arcs
    └── [plan-id]/
        ├── About <plan-name>.md   # cross-language overview
        └── [lang]/                # one subfolder per published language
            ├── requirements.md
            ├── termbase.md
            ├── schedule.md
            ├── days/
            ├── communications/
            └── assets/
```

Each output file's frontmatter records which `2-RAILS/` packages it was generated from, enforcing the citation chain through to the final artefact. Transformations are generated only from packages whose `status` is `complete`. Draft or partial packages are not used.

Full rules in [`../../3-TRANSFORMATIONS/About Transformations.md`](../../3-TRANSFORMATIONS/About Transformations.md).

### `4-SYSTEM/`

Operational infrastructure for both human contributors and the LLM. This folder is **read-only for the LLM** — it specifies the rules but is not edited as part of normal work.

Subfolders:

- `Guidelines/` — cross-cutting methodology docs that don't belong to any single layer: this file, [`why-rails.md`](why-rails.md), and the per-text [`vault-annex.md`](vault-annex.md). Layer-specific rules (1-SOURCES, 2-RAILS, 3-TRANSFORMATIONS) live in each folder's own `About <FolderName>.md`.
- `Skills/` — packaged workflows the LLM invokes for repeatable tasks (e.g. `epub-to-markdown`, `verse-context`, `glossary-combine`, `glossary-select`). See `Skills/SKILLS-CATALOG.md` for the full list.
- `Templates/` — blank-file templates for each frontmatter type, organised by target folder.
- `How-to guides/` — human-facing instructions for non-AI tasks (vault setup, sync troubleshooting, transcription workflows).
- `gemini-scribe/` — Gemini Scribe plugin workspace (`AGENTS.md`, Prompts/, Scheduled-Tasks/, Background-Tasks/, Agent-Sessions/, Skills/).
- `CLAUDE.md` — condensed, LLM-facing operational instructions covering the most important rules from the folder READMEs, plus standard procedures.

---

## 4. The Citation Chain

```
1-SOURCES/  →  2-RAILS/  →  3-TRANSFORMATIONS/
```

Direction is one-way and never skipped:

- `2-RAILS/` cites `1-SOURCES/` only — never another rails file, never parametric knowledge, never `3-TRANSFORMATIONS/`.
- `3-TRANSFORMATIONS/` cites `2-RAILS/` only — never reaching past the rails directly into the sources. (Plan tracks may also embed other completed `3-TRANSFORMATIONS/` outputs — e.g. a daily-readings file embedding the Translation output for its language — recorded the same way in `context_packages:`.)

This rule is the heart of the methodology. It guarantees that every claim in any generated output is traceable back to a specific passage in a specific human source, through an intermediate package that a domain specialist has reviewed.

If a claim cannot be cited, it is not added. The field is left blank and the file's `status` remains `draft`.

---

## 5. Write Permissions

| Folder              | LLM may write? | Notes                                                                                       |
| ------------------- | -------------- | ------------------------------------------------------------------------------------------- |
| `0-INBOX/`          | yes            | scratch only — never cited from elsewhere                                                   |
| `1-SOURCES/`        | **no**         | read-only ground truth; only metadata additions allowed via skill workflows                 |
| `2-RAILS/`          | yes            | primary work area                                                                           |
| `3-TRANSFORMATIONS/`| yes            | only when explicitly instructed; only from `complete` packages                              |
| `4-SYSTEM/`         | **no**         | read-only; rule changes require human contributor action                                    |

The `1-SOURCES/` restriction is the most important. The folder receives the human material once, has its block IDs and frontmatter added under controlled workflows, and is then frozen. Adding interpretation here — even something as small as a paraphrase or a glossing parenthetical — corrupts the ground truth and breaks the citation chain.

---

## 6. Language Tags and Filenames

Every file carrying language-specific content carries a language tag suffix on its filename: `-sk` (Sanskrit IAST default), `-pi` (Pāli PTS default), `-bo` (Tibetan Unicode default), `-zh` (Chinese Unicode default), `-en` (English), and so on. When a non-default script or encoding is used, a script suffix is added: `-sk-iast`, `-bo-wy`, `-zh-cbeta`.

Filenames are lowercase, hyphenated, and use no diacritics. Diacritics appear freely inside file content and frontmatter, but never in filenames — this keeps the vault portable across filesystems and friendly to scripts that traverse it.

The full tag list and naming conventions are specified in [`../../1-SOURCES/About Sources.md`](../../1-SOURCES/About Sources.md) §13.

---

## 7. Block IDs — The Verse-Level Link

Every verse or discrete prose block in `1-SOURCES/` ends with an Obsidian block ID. This is the sole mechanism for cross-file references at the verse level across the entire vault.

```
[verse text here] ^1-1
```

- Format: `^chapter-verse` (most common), `^verse`, or `^book-chapter-verse` — declared per file in the `verse_id_format` frontmatter field.
- Numbers are not zero-padded. Use natural numbers (`^6-33`, not `^06-033`).
- Verse numbers restart at 1 each chapter.
- Pre-chapter material (homage, colophons, title lines) is placed under a `## 0. Introduction` heading with IDs `^0-1`, `^0-2`, etc.

Headings in source-text files also carry block IDs, distinguished from content IDs by a trailing `-0` (the zero slot is reserved for headings; content always starts at `1`). The full heading-ID hierarchy is specified in [`../../1-SOURCES/About Sources.md`](../../1-SOURCES/About Sources