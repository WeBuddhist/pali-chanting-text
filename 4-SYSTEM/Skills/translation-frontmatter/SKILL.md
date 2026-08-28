---
name: translation-frontmatter
description: Generates complete YAML frontmatter for a translation file in 1-SOURCES/Translations/ by extracting metadata from the file's title page, colophon, and opening content.
---

# Translation Frontmatter Creator

This skill populates the standard YAML frontmatter for a translation file (`file_type: translation`) in `1-SOURCES/Translations/`. It extracts all available metadata from the file's title, colophon, and opening content, then writes the complete frontmatter block according to the spec in `1-SOURCES/About Sources.md` §4.

## Instructions

When asked to add or generate frontmatter for a translation file:

1. **Read the file.** Read the target file, focusing on the title page, translator credits, colophon, and opening lines. Do not read the entire body text.
2. **Identify the translator(s).** Record names in `Surname, Firstname` format, separated by semicolons if multiple. Use the name as it appears in the source.
3. **Identify the target language.** This is the language the text was translated *into*. Assign the correct `lang_tag` from §12 of `1-SOURCES/About Sources.md`.
4. **Identify the root text.** Determine which root text this is a translation of and record its vault path under `root_text`. If the corresponding file does not yet exist, leave a descriptive placeholder string (e.g., `"1-SOURCES/Text/[lang]-root-text.md — to be created"`).
5. **Determine `verse_id_format`.** Block IDs in a translation correspond to the *source* verse numbering, not the translator's own numbering. Inspect the root text or notes to confirm the format (`chapter-verse`, `verse`, or `book-chapter-verse`).
6. **Record `translation_basis`.** Note the edition or manuscript the translator worked from, as stated in the preface or colophon.
7. **Record `covers_verses`** if the translation covers a known range (e.g., `1-1–10-58`). Omit if unclear.
8. **Write the frontmatter** by inserting or replacing the YAML block at the top of the file.

## Frontmatter Template

```yaml
---
title:                        # title of the translation as it appears in the file
translator:                   # Surname, Firstname; Surname, Firstname (semicolon-separated)
date:                         # publication year or decade, e.g. 1995
language:                     # target language, e.g. English / French / German
file_type: translation
lang_tag:                     # ISO tag from §12, e.g. en / fr / de
verse_id_format:              # chapter-verse | verse | book-chapter-verse
root_text:                    # vault path to the root text, e.g. 1-SOURCES/Text/[lang]-root-text.md
translation_basis:            # edition the translator worked from, e.g. "[editor year] edition"
covers_verses:                # verse range in block-ID format, e.g. 1-1–10-58 — omit if unknown
source_description:           # REQUIRED — e.g. "[publisher year] first edition"
source_url:                   # URL if sourced digitally — leave blank if none
---
```

## Example Output

```yaml
---
title: [Translation title]
translator: [Surname, Firstname; Surname, Firstname]
date: [year]
language: [target language]
file_type: translation
lang_tag: [tag]
verse_id_format: chapter-verse
root_text: 1-SOURCES/Text/[lang]-root-text.md
translation_basis: [editor year] edition
covers_verses: 1-1–10-58
source_description: "[publisher year] first edition"
source_url:
---
```

## Rules & Edge Cases

- **`source_description` is required.** Every translation file must have it. If publication data is not visible, use `"Source unknown — to be verified"`.
- **Block IDs follow the source verse, not the translator's numbering.** If the translator uses a different verse numbering system, note this with `[Ed: ...]` in the file body — the `verse_id_format` field always refers to the root text's structure.
- **`translator` not `author`.** Translations use the `translator` field. The original author is identified via the `root_text` link.
- **`lang_tag` is the *target* language.** For an English translation, `lang_tag: en`. The source language is implicit in the `root_text` link.
- **Do not hallucinate fields.** If `translation_basis`, `covers_verses`, or `source_url` cannot be confirmed from the file, omit those fields rather than guessing.
- **Omit empty optional fields.** Either populate a field or remove the key entirely.
- **Multiple translators** — list all on a single line, semicolon-separated, as they appear in the publication.
