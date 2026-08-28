---
name: interlinear-gloss
description: For one root text + one translation, build an interlinear gloss file at 2-RAILS/Bilingual-Glossaries/Raw/<source>-<target>-gloss.md. Each verse becomes a ```gloss``` block in the Obsidian Interlinear Glossing plugin format (\gla / \glb / \ex), pairing source tokens against token-by-token target glosses and the translator's free translation. Run once per translation. The output is what glossary-extract-raw reads to catalogue keyword renderings.
---

# interlinear-gloss

This skill creates the **interlinear gloss file** that pairs one root text against one translation, verse by verse. Each verse is rendered as a three-line `gloss` block:

- `\gla` — source-language tokens. Long compounds may be split into their component parts when that helps the alignment.
- `\glb` — token-by-token gloss in the target language, one entry per `\gla` token, lined up by position. **Every word used in `\glb` must come verbatim from the translator's `\ex` line — or from a rounded-bracketed fallback if a designated reference translation is used.**
- `\ex` — the translator's free translation of the verse, verbatim from the translation file.

A gloss block is the **token-level alignment** that all downstream bilingual glossary work depends on. `glossary-extract-raw` reads these files to find keyword renderings; `local-wiki-article` cites them when documenting how a term is rendered across translations; `glossary-select` consults them when judging whether an attested rendering meets a track's requirements.

This skill is run **once per translation**.

---

## Inputs

- **Root text** — `1-SOURCES/Text/<root-text>.md`.
- **Translation** — one file from `1-SOURCES/Translations/<translation>.md`. Must be block-aligned with the root text (same `^block-id` scheme).

## Output

One file at:

```
2-RAILS/Bilingual-Glossaries/Raw/<source-lang>-<target-lang-tag>-gloss.md
```

`<source-lang>` is the root text's `lang_tag`.
`<target-lang-tag>` is the translation's `lang_tag` exactly.

Examples:

| Translation                                 | Output file                                          |
| ------------------------------------------- | ---------------------------------------------------- |
| `<translation-a>.md` (lang_tag `<tag-a>`) | `2-RAILS/Bilingual-Glossaries/Raw/<src>-<tag-a>-gloss.md` |
| `<translation-b>.md` (lang_tag `<tag-b>`) | `2-RAILS/Bilingual-Glossaries/Raw/<src>-<tag-b>-gloss.md` |

If the file already exists, update in place: keep manually filled `\glb` lines, and only refresh `\gla` and `\ex` from the underlying source files (so re-running this skill after the root text or translation is re-formatted does not lose token-gloss work).

---

## Output file format

```markdown
---
source_file: 1-SOURCES/Text/<root-text>.md
source_language: <src-lang-code>
target_file: 1-SOURCES/Translations/<translation>.md
target_language: <target-lang-name>
target_lang_tag: <target-lang-tag>
translator: <from the translation's frontmatter>
total_verses: <count of gloss blocks>
status: draft
---

# Interlinear gloss — <source-lang> → <target-lang> (<translator short name>)

## ^<block-id>

`​`​`​gloss
\gla    <source token 1>   <source token 2>   <source token 3>   ...
\glb    <target gloss 1>   <target gloss 2>   <target gloss 3>   ...
\ex     <free translation, verbatim from the translation file>
`​`​`

## ^<next block-id>

`​`​`​gloss
...
`​`​`
```

One `##` heading per verse block, using the block ID with the caret. One `gloss` code block per `##` heading. Verse order matches root-text order.

---

## Format rules — Obsidian Interlinear Glossing plugin

The plugin (`Interlinear Glossing` by the Obsidian community) renders ```` ```gloss ```` blocks as aligned columns where every token on the `\gla` line lines up with the token at the same position on `\glb`. For the rendering to be correct:

1. **One token per column.** Splitting is by whitespace on the `\gla` line. The number of whitespace-separated tokens on `\glb` must match `\gla` exactly.
2. **Compounds may be split on `\gla`.** When a source compound is long enough that splitting it produces a cleaner alignment, write its parts as separate space-separated tokens on `\gla` (and add the corresponding gloss cells on `\glb`).
3. **Multi-word concepts are joined with underscores, not spaces.** If a multi-word phrase glosses a single source token, join the words with underscores (e.g., `word1_word2`) so it occupies one column.
4. **Missing glosses and particles use `--` or rounded-bracketed fallbacks, never the source original.** When no word in `\ex` corresponds to a `\gla` token, first check if the term is translated in a designated reference translation. If it is, include the rendering in `()` (e.g., `(fallback_term)`). If no reference translates it, write `--`. Never copy the source token itself into `\glb` as a fallback.
5. **No trailing punctuation on `\gla`.** Period, comma, semicolon, question mark — strip from the token. They re-appear in the `\ex` line via the translation.
6. **`\ex` is verbatim from the translator.** Do not paraphrase, do not normalise punctuation, do not strip footnote markers.
7. **`\glb` draws primarily from `\ex` — with specific fallbacks.** Every `\glb` cell must be a word (or underscore-joined phrase) whose component words all appear verbatim in the `\ex` line for that same block, or come from a bracketed fallback.

### Advanced Glossing Patterns (The "Solutions")

To ensure consistent glossary extraction and clear interlinear reading, follow these patterns for complex cases:

- **The Summary Word Expansion**: When a translator uses a summary word to cover a complex source compound, include the full semantic context in underscores and brackets.
  - Gloss: `summary_word_(context1_context2)`
  - Why: This ensures downstream extraction captures the mapping to the component concepts.

- **Implicit Repetition (Ghosting)**: When the source repeats a term but the translation omits it for brevity, use bracketed repetitions to maintain 1-to-1 alignment.
  - Source: `... token ... token`
  - Gloss: `... term ... (term)`

- **Compound Splitting for Alignment**: If a source compound corresponds to distinct words in the translation, split the compound on the `\gla` line using spaces.
  - Source: `compoundpart1compoundpart2`
  - `\gla`: `part1 part2`
  - `\glb`: `gloss1 gloss2`

- **Underscore Syntax**:
  - Use underscores to join multi-word phrases from `\ex`.
  - Use underscores to link a word to its bracketed clarification.
  - Use standalone brackets for completely omitted repetitions.

---

## Procedure

The recommended path is the scaffold helper followed by an LLM pass for the `\glb` line.

1. **Run the scaffold script:**

   ```bash
   python3 4-SYSTEM/Skills/interlinear-gloss/scripts/scaffold_gloss.py \
       1-SOURCES/Text/<root-text>.md \
       1-SOURCES/Translations/<translation>.md \
       2-RAILS/Bilingual-Glossaries/Raw/<src>-<tag>-gloss.md
   ```

   The script aligns blocks by `^block-id`, emits one `##` heading per paired block, and scaffolds each `gloss` block with `\gla`, `\glb` (placeholders), and `\ex`.

2. **Spot-check the scaffold.** Confirm: every block in the source has a matching `##` heading; `\gla` tokens look clean; the `\ex` line matches the translation file's body. The frontmatter `total_verses` matches the heading count.

3. **Fill `\glb`, verse by verse or in batches.** This is the LLM-driven half. The procedure for each cell is:
   a. Read the `\ex` line for the block.
   b. Find the word or phrase in `\ex` that most directly corresponds to this `\gla` token. Use only words that appear verbatim in `\ex`; join multi-word phrases with underscores.
   c. If the word is a summary or a repetition omitted in `\ex`, apply the **Advanced Glossing Patterns**.
   d. If the term is untranslated in `\ex`, use a designated reference translation fallback in `()`.
   e. If the term is also untranslated in the reference, write `--`.
   f. Where a scaffold token on `\gla` is a long compound that would be clearer split, replace the single compound token with its space-separated parts and extend `\glb` with one cell per part.

4. **Verify column count.** Run the scaffold script with `--validate` to re-check that `\glb` has the same number of whitespace-separated tokens as `\gla` for every block:

   ```bash
   python3 4-SYSTEM/Skills/interlinear-gloss/scripts/scaffold_gloss.py \
       --validate 2-RAILS/Bilingual-Glossaries/Raw/<src>-<tag>-gloss.md
   ```

5. **Set `status: draft`.** A domain specialist marks the file `complete` after review.

---

## Re-running this skill

The scaffold script can be re-run safely:

- Existing `\glb` lines are preserved if their token count still matches `\gla` after the source text is re-read.
- If the source text was re-formatted (e.g. a verse was retokenised), the affected `\glb` lines are reset to `--` placeholders and the change is flagged in stderr so you can review.
- `\gla` and `\ex` are always refreshed from the underlying source files.

---

## How downstream skills consume this file

- `glossary-extract-raw` walks every `gloss` block in this file, pairs `\gla` tokens against `\glb` cells, and records every distinct `(source-token, target-gloss)` rendering.
- `local-wiki-article` may transclude individual gloss blocks (`![[<gloss-file>.md#^block-id]]`) when documenting how a term is rendered across translations.
- `verse-context` may transclude a gloss block as part of the Commentary passages section for the verse.

---

## Completion check

- [ ] One `##` heading per source-text block, in source order
- [ ] One `gloss` code block per `##` heading
- [ ] `\gla`, `\glb`, `\ex` all present in every block
- [ ] Token count matches across `\gla` and `\glb` for every block (use `--validate`)
- [ ] `\ex` is verbatim from the translation file
- [ ] Frontmatter `total_verses` matches the heading count
- [ ] No `\glb` cell contains a source word or a term absent from the corresponding `\ex` line (unless bracketed from a reference or clarification)
- [ ] `--` is used wherever the translation and reference provide no corresponding word — not a source-language fallback
