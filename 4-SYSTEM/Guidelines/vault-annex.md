# Vault Annex — [text-slug] conventions

The methodology guidelines (`0-VAULT-Structure.md`, `../../1-SOURCES/About Sources.md`, `../../2-RAILS/About Rails.md`, `../../3-TRANSFORMATIONS/About Transformations.md`) are **text-agnostic** — they apply to any Railroads vault built on any classical text. This annex records the conventions that are specific to *this* vault: **[name of text]**.

When the Guidelines and this annex disagree on a vault-specific detail, this annex wins.

> **Template instructions:** Fill in each section below, replacing all `[placeholder]` text. Delete this instruction block when done.

---

## 1. The text

This vault serves **[name of text]** — [one-sentence description of the text and its tradition].

Source-text files in `1-SOURCES/Text/` correspond to the following books / volumes:

| Order | Book / Volume | Filename |
| ----- | ------------- | -------- |
| 1 | [Title] | `[lang]-[slug].md` |
| 2 | [Title] | `[lang]-[slug].md` |

Only books that have been ingested are present in the folder. The primary text currently being railed out is **[book / chapter]**.

---

## 2. Addressing scheme

[Describe how block IDs are structured for this text. Use one of the standard schemes from `1-SOURCES/About Sources.md` §5, or document a custom scheme here if the text's structure requires it.]

**`verse_id_format`:** `[chapter-verse | verse | book-chapter-verse | book-verse | custom]`

**Format example:** `^[example]`

### Heading hierarchy

| Markdown | Role | Anchor |
| -------- | ---- | ------ |
| `#` | [e.g. Piṭaka / collection] | `^[slug]-0` |
| `##` | [e.g. Book / volume] | `^[book]-0` |
| `###` | [e.g. Chapter / major section] | `^[book]-[ch]-0` |
| `####` | [Sub-section] | `^[book]-[ch]-[s]-0` |

### Verse numbering rule

[Describe whether verse numbers restart at each chapter boundary, or run continuously through a book, and any exceptions.]

---

## 3. Registered commentary IDs

Every commentary file in `1-SOURCES/Commentaries/` declares a `registered_id` in its frontmatter. That short ID is the only string used to attribute claims to the commentary throughout `2-RAILS/`.

Once assigned, a `registered_id` never changes. New commentaries must be added to the roster below before their `registered_id` is used in any rail.

| `registered_id` | Title | Tier | Language | File |
| --------------- | ----- | ---- | -------- | ---- |
| `[short-id]` | [Commentary title] | [commentary \| sub-commentary \| …] | [Language] | `1-SOURCES/Commentaries/[lang]-[slug].md` |

**Tier ordering** within a verse package's Traditional Interpretation section: [describe the preferred order, e.g. primary commentary first, then sub-commentaries].

---

## 4. Language tracks

| Tag | Language | Translation track | Plan stream |
| --- | -------- | ----------------- | ----------- |
| `[src-tag]` | [Source language] | — (source) | `days/[tag]/` (if applicable) |
| `[tgt-tag]` | [Target language 1] | `[lang]-[descriptor]/` | — |
| `[tgt-tag]` | [Target language 2] | `[lang]-[descriptor]/` | — |

Each translation track's `requirements.md` is written in its own target language. New tracks are added by creating `Translations/[lang]-[descriptor]/` and running the `glossary-select` skill from the consolidated `2-RAILS/Bilingual-Glossaries/[src]-[tgt].md`.

---

## 5. Bilingual glossary pairs

The consolidated bilingual glossaries in `2-RAILS/Bilingual-Glossaries/` cover the following source→target combinations:

| File | Source language | Target language | Status |
| ---- | --------------- | --------------- | ------ |
| `[src]-[tgt].md` | [Source] | [Target] | `draft` |

---

## 6. Active transformation tracks

| Track | Category | Status |
| ----- | -------- | ------ |
| `[lang]-[descriptor]` | Translation | `draft` |
| `[plan-id]` | Plan | `draft` |

---

## 7. Source-language tags used in this vault

| Tag | Script / System | Use in this vault |
| --- | --------------- | ----------------- |
| `-[tag]` | [Script] | [When used] |

The default for every [language] source is `-[default-tag]`.

---

## 8. Where to look next

- [`0-VAULT-Structure.md`](0-VAULT-Structure.md) — the architecture in full.
- [`../../1-SOURCES/About Sources.md`](../../1-SOURCES/About%20Sources.md) — source-file rules.
- [`../../2-RAILS/About Rails.md`](../../2-RAILS/About%20Rails.md) — rails schema.
- [`../../3-TRANSFORMATIONS/About Transformations.md`](../../3-TRANSFORMATIONS/About%20Transformations.md) — track and output rules.
- [Top-level `README.md`](../../README.md) — pipeline overview and reading paths.
