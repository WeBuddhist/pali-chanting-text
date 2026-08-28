---
name: commentary-frontmatter
description: Generates complete YAML frontmatter for a commentary file in 1-SOURCES/Commentaries/ by extracting metadata from the file's title, colophon, and opening content.
---

# Commentary Frontmatter Creator

This skill populates the standard YAML frontmatter for a commentary file (`file_type: commentary`) in `1-SOURCES/Commentaries/`. It extracts all available metadata from the file's title, colophon, and opening content, then writes the complete frontmatter block according to the spec in `1-SOURCES/About Sources.md` §4.

## Instructions

When asked to add or generate frontmatter for a commentary file:

1. **Read the file.** Read the target file, focusing on the title line, author credits, colophon, and opening lines. Do not read the entire body.
2. **Identify the language and script.** Determine the primary language of the commentary (which may differ from the root text) and its script. Assign the correct `lang_tag` from §12 of `1-SOURCES/About Sources.md`.
3. **Assign a `registered_id`.** This is the short, stable identifier used in `2-RAILS/` to attribute claims to this commentary. Derive it from the author's surname in lowercase, romanised without diacritics. Once set it must never change. Check the vault annex (`4-SYSTEM/Guidelines/vault-annex.md` §Commentaries) to confirm the ID is not already taken.
4. **Identify the root text.** Record the vault path of the root text this commentary addresses under `root_text`.
5. **Determine `verse_id_format`.** This field declares the commentary's *own* internal numbering system — not the root text's. Inspect how the commentary structures its own divisions:
   - Chapter + verse → `chapter-verse`
   - Section + paragraph → `section-paragraph`
   - Single sequential verse/passage number → `verse`
   - Folio + line → `folio-line`
   - Book + chapter + verse → `book-chapter-verse`
   If the commentary has no internal numbering, use `verse` and apply sequential numbering.
6. **Record `covers_verses`** — the range of root text verses this commentary addresses, in block-ID format (e.g., `1-1–10-58`). Omit if the range is unclear.
7. **Add external IDs** (BDRC, GRETIL, etc.) only when they are visible in the file itself.
8. **Write the frontmatter** by inserting or replacing the YAML block at the top of the file.

## Frontmatter Template

```yaml
---
title:                        # exact title of the commentary (diacritics OK)
author:                       # commentary author (diacritics OK)
date:                         # date or century of composition, e.g. "11th century CE"
language:                     # language of the commentary, e.g. Sanskrit / Tibetan / English
script:                       # script name — omit for roman-script languages
file_type: commentary
lang_tag:                     # ISO tag from §12, e.g. sk / bo / en
verse_id_format:              # the commentary's own ID system (see §9 of About Sources.md)
registered_id:                # short stable ID used in 2-RAILS/ — lowercase, no diacritics
root_text:                    # vault path to the root text, e.g. 1-SOURCES/Text/[lang]-root-text.md
covers_verses:                # root text verse range, e.g. 1-1–10-58 — omit if unknown
source_description:           # REQUIRED — e.g. "Transcribed from [editor year] edition"
source_url:                   # URL if sourced digitally — leave blank if none
bdrc_work_id:                 # omit if unknown
bdrc_instance_id:             # omit if unknown
gretil_url:                   # GRETIL URL — omit if not applicable
dsbc_url:                     # DSBC URL — omit if not applicable
cbeta_id:                     # Chinese Buddhist canon — omit if not applicable
acip_id:                      # Tibetan ACIP — omit if not applicable
other_ids:                    # VIAF, Wikidata, etc. — omit if none
---
```

## Example Output

```yaml
---
title: [Commentary title]
author: [Commentator]
date: [century or year]
language: [language]
script: [script — omit for roman-script languages]
file_type: commentary
lang_tag: [tag]
verse_id_format: chapter-verse
registered_id: [short-id]
root_text: 1-SOURCES/Text/[lang]-root-text.md
covers_verses: 1-1–10-58
source_description: "Transcribed from [editor year] edition"
---
```

## Rules & Edge Cases

- **`source_description` is required.** Every commentary file must have it. If publication data is not visible, use `"Source unknown — to be verified"`.
- **`registered_id` must be unique and stable.** Check the vault annex (`4-SYSTEM/Guidelines/vault-annex.md` §Commentaries) before assigning. Once a commentary is used in any `2-RAILS/` file, the `registered_id` must never change. After writing the frontmatter, remind the user to register the new ID in the vault annex.
- **`verse_id_format` is the commentary's own system, not the root text's.** A Tibetan commentary may use `folio-line` even though a Sanskrit root text uses `chapter-verse`. Both coexist — root text transclusions in the commentary body carry the root text's block IDs, while the commentary's own passages carry its own IDs.
- **`script` field** — include for non-roman scripts (Devanāgarī, Unicode Tibetan, etc.). Omit for languages written in the Latin alphabet.
- **Do not hallucinate external IDs.** If a BDRC, GRETIL, or other ID is not visible in the file, omit that field entirely.
- **Omit empty optional fields.** Either populate a field or remove the key entirely — no `null` or `""` placeholders.
