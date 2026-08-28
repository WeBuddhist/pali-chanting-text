---
name: root-text-frontmatter
description: Generates complete YAML frontmatter for a root text file in 1-SOURCES/Text/ by extracting metadata from the file's title, colophon, and opening content.
---

# Root Text Frontmatter Creator

This skill populates the standard YAML frontmatter for a root text file (`file_type: root-text`) in `1-SOURCES/Text/`. It extracts all available metadata from the file's title, colophon, and opening lines, then writes the complete frontmatter block according to the spec in `1-SOURCES/About Sources.md` §4.

## Instructions

When asked to add or generate frontmatter for a root text file:

1. **Read the file.** Read the target file, focusing on the title line, the opening verse or prose, and the colophon (publication information found at the beginning or end). Do not read the entire body.
2. **Determine the language and script.** Identify the primary language (Sanskrit, Tibetan, Chinese, Pāli, etc.) and the script in use. Assign the correct `lang_tag` from the table in §12 of `1-SOURCES/About Sources.md`.
3. **Extract all available fields** (see template below). Only include external ID fields (`bdrc_work_id`, `dsbc_url`, etc.) when the values are visible in the file itself — never invent them.
4. **Determine `verse_id_format`.** Inspect the file structure:
   - Verses numbered by chapter and verse → `chapter-verse`
   - Verses carrying a single sequential number → `verse`
   - Text with books, chapters, and verses → `book-chapter-verse`
5. **Count or estimate** `chapters` and `total_verses` if the file makes them clear. Omit if uncertain.
6. **Populate `related_commentaries` and `related_translations`** only if corresponding files already exist in `1-SOURCES/`. Use full vault paths.
7. **Write the frontmatter** by inserting or replacing the YAML block at the top of the file.

## Frontmatter Template

```yaml
---
title:                        # exact title as it appears in the file (diacritics OK)
author:                       # original author name (diacritics OK)
date:                         # date or century of composition, e.g. "8th century CE"
language:                     # full language name, e.g. Sanskrit / Tibetan / Chinese
script:                       # script name, e.g. Devanāgarī / Unicode Tibetan
file_type: root-text
lang_tag:                     # ISO tag from §12, e.g. sk / bo / zh / pi
chapters:                     # integer — omit if unknown
total_verses:                 # integer — omit if unknown
verse_id_format:              # chapter-verse | verse | book-chapter-verse
source_description:           # REQUIRED — e.g. "Transcribed from [editor year] critical edition"
source_url:                   # URL if sourced digitally — leave blank if none
dsbc_url:                     # DSBC entry URL — omit if not applicable
bdrc_work_id:                 # e.g. WA######## — omit if unknown
bdrc_instance_id:             # omit if unknown
gretil_url:                   # GRETIL URL — omit if not applicable
cbeta_id:                     # Chinese Buddhist canon — omit if not applicable
suttacentral_id:              # Pāli texts — omit if not applicable
acip_id:                      # Tibetan ACIP — omit if not applicable
other_ids:                    # VIAF, Wikidata, etc. — omit if none
related_commentaries:         # list of vault paths — omit if none yet
related_translations:         # list of vault paths — omit if none yet
---
```

## Example Output

```yaml
---
title: [Root text title]
author: [Author]
date: [century or year of composition]
language: [language]
script: [script]
file_type: root-text
lang_tag: [tag]
chapters: [N]
total_verses: [N]
verse_id_format: chapter-verse
source_description: "Transcribed from [editor year] critical edition"
source_url: [url — omit if none]
related_commentaries:
  - 1-SOURCES/Commentaries/[commentary]-[tag].md
related_translations:
  - 1-SOURCES/Translations/[translation]-[tag].md
---
```

## Rules & Edge Cases

- **`source_description` is required.** Every root text file must have it. If no publication data is visible, use a minimal description such as `"Source unknown — to be verified"`.
- **Do not hallucinate external IDs.** If a BDRC, GRETIL, DSBC, or other ID is not visible in the file, omit that field entirely.
- **One script per file.** If the file contains an alternative script (e.g., IAST alongside Devanāgarī), note the discrepancy with `[Ed: ...]` — do not add a second script tag.
- **`lang_tag` follows §12 of About Sources.md.** For editions in an alternative script, append the script suffix (e.g., `sk-iast`, `bo-wy`).
- **Omit empty optional fields.** Do not leave placeholder values like `null` or `""`. Either populate a field or remove the key entirely.
- **`related_commentaries` / `related_translations`** — list only files that already exist in the vault. Do not pre-populate with anticipated future files.
