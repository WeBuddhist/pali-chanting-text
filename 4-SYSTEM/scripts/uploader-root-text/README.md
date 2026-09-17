# Uploader — Root Text

Submits the payloads the parser produced to the library API and records the
returned ids back into the source `.md`.

## Input

A **parser output folder** — everything the uploader needs is in it:

```
4-SYSTEM\scripts\parser-root-text\output\तिसरण–पञ्चशील_hi\
    तिसरण–पञ्चशील_hi.text.json        -> step 1
    तिसरण–पञ्चशील_hi.edition.json     -> step 2
    तिसरण–पञ्चशील_hi.toc.json         -> step 3
    तिसरण–पञ्चशील_hi.alignment.json   -> step 4 (translations/commentaries only)
    तिसरण–पञ्चशील_hi.ids.json         <- written back by this script
```

A source `.md` path or a bare stem is also accepted; both resolve to the same
folder. The folder name is the stem, and the source `.md` is located by that
stem under `1-SOURCES/` (NFC/NFD tolerant) so ids can be written into its
frontmatter — the upload still runs if it isn't found.

## What it does

For each input folder, in order:

| # | Step | Call | Returns |
|---|------|------|---------|
| 1 | text | `POST /v2/texts` | `{"id": …}` → `text_id` |
| 2 | edition | `POST /v2/texts/{text_id}/editions` | `{"id": …}` → `edition_id` |
| 3 | table of contents | `POST /v2/editions/{edition_id}/table-of-contents` | `{"id": …}` → `toc_id` |
| 4 | alignment | `PUT /v2/editions/{edition_id}/alignments/{root_edition_id}` | `204 No Content` |

Then it patches `text_id`, `edition_id` and `toc_id` into the source file's YAML
frontmatter.

## Output

```
==============================================================
  तिसरण–पञ्चशील_hi.md
    text_id     : mRq8…
    edition_id  : Kf2p…
    toc_id      : 9dTa…
    alignment   : Kf2p… -> U0RlyyaJsKNcKcAAtQUur  (HTTP 204, no id returned)
==============================================================
```

**There is no `alignment_id`.** Step 4 is a `PUT` keyed by the two edition ids —
an upsert of the alignment between this edition and the root's — so the API
answers `204 No Content` with no body. The pair of edition ids *is* the
identity; re-running replaces the alignment rather than creating a second one.

## Requirements

```
pip install PyYAML
```

Python 3.8+. No other dependencies — HTTP goes through `urllib`.

## API key

Most endpoints require an `X-API-Key` header:

```bash
set WEBUDDHIST_API_KEY=…          # Windows (cmd)
$env:WEBUDDHIST_API_KEY = "…"     # Windows (PowerShell)
export WEBUDDHIST_API_KEY=…       # bash
```

or pass `--api-key …`. If neither is set the header is omitted, which works
only for endpoints that are open.

## How to run

Run the linter and the parser first, then:

```bash
python 4-SYSTEM\scripts\uploader-root-text\upload.py "4-SYSTEM\scripts\parser-root-text\output\तिसरण–पञ्चशील_hi"
```

Several files at once are fine. **Upload a root text before its translations** —
step 4 reads the root's `edition_id` out of the file named by `root_text:`.

### Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | print every call and payload size, send nothing |
| `--force` | create new records even when the frontmatter already has ids |
| `--skip-alignment` | stop after the TOC |
| `--api-key KEY` | `X-API-Key` header (or `WEBUDDHIST_API_KEY`) |
| `--base-url URL` | default `https://library.webuddhist.com` |
| `--root-edition-id ID` | step 4's target, when the source `.md` can't be found |

## Notes

- **Re-running is safe.** Any step whose id is already in the frontmatter is
  skipped, so a second run does not create duplicates. `--force` overrides this
  and leaves the old records orphaned in the API
- Step 4 is skipped with a warning, not an error, when there is no
  `alignment.json` (root texts), when `root_text:` cannot be resolved, or when
  the root has no `edition_id` yet
- Ids are recorded in `<stem>.ids.json` inside the payload folder **and** in the
  source `.md` frontmatter. Either one makes a re-run skip that step; the
  frontmatter wins when they disagree
- The frontmatter patch preserves the file's existing line endings, so a CRLF
  file does not turn into a whole-file diff
- Any non-2xx response aborts that file and prints the API's error body — the
  `422` shape is `{"detail": [{"loc": …, "msg": …, "type": …}]}`
