# Adaptations

Audience-targeted retellings of the text — a children's version, a scholarly summary, a meditation manual, a sermon series. An adaptation is a **domain shift, not necessarily a language shift**: it restructures or reframes the source for an audience that needs more (or less) than the source provides at face value.

Each subfolder is one **adaptation track** — one (audience × shape × purpose) combination — and contains:

```
Adaptations/
└── <track-id>/
    ├── requirements.md # audience, shape, scope, what to keep, what to dissolve
    ├── audience.md     # the audience profile
    ├── termbase.md     # (optional) locked renderings
    └── <output>.md    # the generated adaptation files
```

For the category-wide convention (what `requirements.md` must contain, the citation chain, the status lifecycle), see [`../About Transformations.md`](../About Transformations.md).

---

## Per-track convention

### `requirements.md`

Required. Written in the working language of the adaptation team. Must cover:

- **Audience** — age, prior knowledge, reading context (e.g. children 8–12 at a Sunday-school class, scholars writing literature reviews, lay practitioners on retreat).
- **Structural shape** — what does the output look like? A series of stories? A FAQ? A chapter-by-chapter retelling? A weekly sermon cycle?
- **Treatment policy** — what to keep verbatim, what to paraphrase, what to dissolve into prose, what to footnote, what to omit entirely. Be explicit about doctrinal claims: which to preserve, which to soften, which to leave out.
- **Cultural-adaptation rules** — terms that translate, terms that gloss, terms that stay untranslated with a definition box.
- **Source-rail dependencies** — which rails (`Sections/`, `Verses/`, `Local-Wiki/`) the adaptation skill must consult.

### `termbase.md`

Many adaptations work directly from the rails without a separate locked-rendering termbase — the adaptation is doing freer work than a translation and benefits from picking the right word for each context rather than enforcing a single mapping. Include a `termbase.md` only when an adaptation locks specific renderings.

When present, the termbase follows the same format as a translation termbase — see [`../Translations/About Translations.md`](../Translations/About Translations.md).

---

## Current tracks

No tracks exist yet — the folder is reserved for the next round of work. Add new tracks as they are commissioned.

---

## File-level rules

- Each output file's frontmatter cites the rails it was generated from (and any prior-track outputs it built on — e.g. an adaptation may build on a completed translation).
- Only `status: complete` adaptation files are referenced by other transformations.
- The citation chain (`1-SOURCES/` → `2-RAILS/` → `3-TRANSFORMATIONS/`) is enforced; an adaptation may not reach past the rails to cite `1-SOURCES/` directly.
