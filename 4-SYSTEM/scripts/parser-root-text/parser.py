#!/usr/bin/env python3
"""Parse linter output files and produce clean API-ready payloads."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


OUTPUT_DIR = Path(__file__).parent / "output"

YAML_PROPS_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
REF_RE = re.compile(r'(\^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?)\s*$')
ROMAN_RE = re.compile(r'^[IVXLCDM]+$')
VERSE_X_RE = re.compile(r'\d+[xX]\d+')
TRANSCLUSION_RE = re.compile(r'^\s*!\[\[.*?#\^.*?\]\]\s*$')
_TRANS_REF_RE = re.compile(r'!\[\[.*?#\^([A-Za-z0-9]+(?:-[A-Za-z0-9]+)?)\]\]')
_WYLIE_RE = re.compile(r"'[a-zA-Z]")


def _wylie_to_unicode(text, lang_tag):
    if lang_tag != "bo":
        return text
    if not text or any("ༀ" <= c <= "࿿" for c in text):
        return text
    if not _WYLIE_RE.search(text):
        return text
    try:
        import pyewts as _pyewts
        converter = _pyewts.pyewts()
        converted = converter.toUnicode(text)
        if converted and converted.strip():
            return converted
    except ImportError:
        pass
    return text


def _out_path(stem, kind):
    """Output path for one payload: ``output/<stem>/<stem>.<kind>.json``.

    Every payload for a given text lands in its own folder, so a text's
    four files stay together instead of interleaving in a flat directory.
    """
    out_dir = OUTPUT_DIR / stem
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{stem}.{kind}.json"


def _apply_bold(text, as_tag=True):
    """Whole-span bold: ``**X**`` -> ``<b>X</b>``.

    Only fires when the text both starts and ends with ``**``; anything else
    is returned untouched. Applied before character offsets are computed, so
    the segmentation spans always describe the text as emitted.

    ``as_tag=False`` strips the markers without emitting a tag — used for
    heading text, which becomes a plain TOC label rather than content.
    """
    if not text:
        return text
    stripped = text.strip()
    if len(stripped) > 4 and stripped.startswith("**") and stripped.endswith("**"):
        inner = stripped[2:-2]
        if inner.strip():
            return "<b>" + inner + "</b>" if as_tag else inner
    return text


def _is_empty(value):
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, dict)) and not value:
        return True
    return False


def _read_source(path):
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit("PyYAML is required: pip install pyyaml") from exc
    text = path.read_bytes().replace(b'\x00', b'').decode("utf-8", errors="replace")
    m = YAML_PROPS_RE.match(text)
    if not m:
        raise ValueError("no YAML properties found")
    data = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():]
    return data, body


def _resolve_root_text_path(val, source_path):
    val_path = Path(val)
    for base in [source_path.parent, *source_path.parents]:
        candidate = base / val_path
        if candidate.exists():
            return candidate
    name = val_path.name
    for base in source_path.parents:
        matches = list(base.rglob(name))
        if matches:
            return matches[0]
    return None


def _extract_blocks(body):
    blocks = []
    for raw in re.split(r'\r?\n[ \t]*\r?\n', body.strip()):
        block = raw.strip()
        if not block:
            continue
        lines = [l.rstrip('\r') for l in block.split('\n')]
        is_header = lines[0].lstrip().startswith('#')
        ref = None
        for line in reversed(lines):
            stripped = line.rstrip()
            if stripped:
                m = REF_RE.search(stripped)
                if m:
                    ref = m.group(1)
                break
        blocks.append({"ref": ref, "is_header": is_header, "lines": lines, "raw": block})
    return blocks


def _extract_header_levels(body):
    result = {}
    for line in body.split('\n'):
        stripped = line.rstrip('\r').rstrip()
        if not stripped.startswith('#'):
            continue
        level = len(stripped) - len(stripped.lstrip('#'))
        text_with_ref = stripped.lstrip('#').strip()
        m = REF_RE.search(text_with_ref)
        if m:
            result[m.group(1).lstrip('^')] = level
    return result


def _infer_segment_type(ref_no_caret, doc_default):
    if not ref_no_caret:
        return doc_default
    if ref_no_caret[0].upper() == 'T':
        return "top_segment"
    parts = ref_no_caret.split('-')
    first = parts[0]
    if ROMAN_RE.match(first):
        return "front_matter"
    if VERSE_X_RE.search(ref_no_caret):
        return "verse"
    for part in parts:
        if part and not part.isdigit() and not ROMAN_RE.match(part):
            return "back_matter"
    return doc_default


# ---------------------------------------------------------------------------
# Function 1: extract text_input
# ---------------------------------------------------------------------------

def extract_text_input(lint_path, out_stem=None):
    data = json.loads(
        lint_path.read_bytes().replace(b'\x00', b'').decode("utf-8", errors="replace")
    )
    text_input = data.get("text_input") or data.get("resolved")
    if text_input is None:
        raise ValueError(f"no text_input found in {lint_path.name}")
    clean = {k: v for k, v in text_input.items() if not _is_empty(v)}

    if "alt_titles" not in clean:
        print("  WARN alt_titles: missing — ignored", file=sys.stderr)

    contribs = clean.get("contributions")
    if contribs is None:
        print("  WARN contributions: author/translator missing — ignored", file=sys.stderr)
    elif isinstance(contribs, list):
        kept = []
        for i, entry in enumerate(contribs):
            if not isinstance(entry, dict):
                print(f"  WARN contributions[{i}]: invalid entry — skipped", file=sys.stderr)
                continue
            role = entry.get("role", "contributor")
            if entry.get("type") == "ai":
                if entry.get("id") or entry.get("ai_id"):
                    kept.append(entry)
                else:
                    print(
                        f"  WARN {role}: AI contributor missing id — skipped",
                        file=sys.stderr,
                    )
                continue
            if entry.get("id") or entry.get("bdrc_id"):
                kept.append(entry)
            else:
                print(
                    f"  WARN {role}: not found (no id) — skipped",
                    file=sys.stderr,
                )
        if kept:
            clean["contributions"] = kept
        else:
            clean.pop("contributions", None)
            if contribs:
                print(
                    "  WARN contributions: none had resolvable ids — omitted",
                    file=sys.stderr,
                )

    stem = lint_path.stem
    if stem.endswith(".lint"):
        stem = stem[:-len(".lint")]
    # Prefer the source .md stem so every payload shares one output folder
    # even when the lint file was renamed.
    out_path = _out_path(out_stem or stem, "text")
    out_path.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Function 2: build edition
# ---------------------------------------------------------------------------

def _build_content_and_segmentation(blocks, doc_default):
    parts = []
    seg_list = []
    heading_list = []
    pos = 0

    for block_num, block in enumerate(blocks, start=1):
        ref = block["ref"]
        raw_lines = block["lines"]
        is_header = block["is_header"]

        content_lines = [l for l in raw_lines if not TRANSCLUSION_RE.match(l)]
        # Pure transclusion block — silently skip, used for alignment only
        if not any(l.strip() for l in content_lines):
            continue

        if not ref:
            print(f"  WARN block {block_num}: no reference marker — skipped", file=sys.stderr)
            continue

        ref_no_caret = ref[1:] if ref.startswith("^") else ref

        if is_header:
            # Headings are structural only — their text is NOT emitted into
            # the edition content. Record the title, its level, and the
            # content offset at which this heading's section begins, for
            # build_toc to consume.
            raw_head = raw_lines[0].lstrip()
            level = len(raw_head) - len(raw_head.lstrip('#'))
            text = raw_head.lstrip('#').strip()
            ref_idx = text.rfind(ref)
            if ref_idx != -1:
                text = text[:ref_idx].rstrip()
            if not text:
                continue
            heading_list.append({
                "reference": ref_no_caret,
                "title": _apply_bold(text, as_tag=False),
                "level": level or 1,
                "content_start": pos,
            })
        else:
            line_spans = []
            for raw_line in content_lines:
                text = raw_line.rstrip()
                # Strip a trailing block-id marker (e.g. "^1-2") from every
                # line, not just the segment's own closing reference line —
                # per-line anchors used for finer-grained IDs must not leak
                # into the joined edition content.
                m = REF_RE.search(text)
                if m:
                    text = text[:m.start()].rstrip()
                if not text:
                    continue
                text = _apply_bold(text)
                start = pos
                parts.append(text)
                pos += len(text)
                line_spans.append({"start": start, "end": start + len(text)})
            seg_type = _infer_segment_type(ref_no_caret, doc_default)
            seg_list.append({"lines": line_spans, "type": seg_type, "reference": ref_no_caret})

    return "".join(parts), seg_list, heading_list


def build_edition(source_path, lint_path):
    fm, body = _read_source(source_path)
    blocks = _extract_blocks(body)

    file_type = fm.get("file_type", "")
    if file_type == "translation":
        root_text_val = fm.get("root_text")
        root_file_type = None
        if root_text_val:
            resolved_root = _resolve_root_text_path(str(root_text_val), source_path)
            if resolved_root:
                try:
                    root_fm, _ = _read_source(resolved_root)
                    root_file_type = root_fm.get("file_type", "")
                except (ValueError, OSError):
                    pass
        doc_default = "paragraph" if root_file_type == "commentary" else "verse"
    else:
        doc_default = "paragraph" if fm.get("commentary_of") else "verse"

    content_str, seg_list, heading_list = _build_content_and_segmentation(
        blocks, doc_default
    )

    edition_type = fm.get("edition_type", "critical")
    source_url = (
        fm.get("source") or fm.get("gretil_url") or fm.get("dsbc_url")
        or fm.get("suttacentral_id") or ""
    )
    metadata = {"type": edition_type, "source": source_url}

    out = {
        "metadata": metadata,
        "content": content_str,
        "segmentation": {"segments": seg_list},
    }

    out_path = _out_path(source_path.stem, "edition")
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    # Headings are not part of the edition payload — they are handed to
    # build_toc in memory only, never written to <stem>.edition.json.
    result = dict(out)
    result["headings"] = heading_list
    return out_path, result


# ---------------------------------------------------------------------------
# Function 3: build TOC
# ---------------------------------------------------------------------------

def build_toc(source_path, edition_result):
    fm, body = _read_source(source_path)
    lang_tag = fm.get("lang_tag") or "en"

    content_len = len(edition_result["content"])
    headings = edition_result.get("headings") or []
    header_levels = _extract_header_levels(body)

    title_nodes = []
    for heading in headings:
        ref = heading.get("reference", "")
        level = header_levels.get(ref, heading.get("level", 1))
        # Heading text no longer lives inside the edition content, so a
        # section's span starts where its content starts.
        title_nodes.append({
            "level": level,
            "span_start": heading["content_start"],
            "title": _wylie_to_unicode(heading.get("title", ""), lang_tag),
            "ref": ref,
        })

    for i, node in enumerate(title_nodes):
        span_end = content_len
        for j in range(i + 1, len(title_nodes)):
            if title_nodes[j]["level"] <= node["level"]:
                span_end = title_nodes[j]["span_start"]
                break
        node["span_end"] = span_end

    def _nest(nodes, idx, parent_level):
        sections = []
        i = idx
        while i < len(nodes):
            node = nodes[i]
            if node["level"] <= parent_level:
                break
            if node["level"] == parent_level + 1:
                section = {
                    "title": {lang_tag: node["title"]},
                    "span": {"start": node["span_start"], "end": node["span_end"]},
                }
                subsections, i = _nest(nodes, i + 1, node["level"])
                if subsections:
                    section["subsections"] = subsections
                sections.append(section)
            else:
                i += 1
        return sections, i

    top_level = title_nodes[0]["level"] if title_nodes else 1
    sections, _ = _nest(title_nodes, 0, top_level - 1)

    out = {"sections": sections}



    out_path = _out_path(source_path.stem, "toc")
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path, out


# ---------------------------------------------------------------------------
# Function 4: build alignment (translation/commentary only)
# ---------------------------------------------------------------------------

def build_alignment(source_path):
    fm, body = _read_source(source_path)
    file_type = fm.get("file_type", "")
    if file_type not in ("translation", "commentary"):
        raise ValueError(
            f"alignment only applies to translation/commentary files, got file_type={file_type!r}"
        )

    alignments = []
    seen_pairs = set()
    blocks = _extract_blocks(body)
    pending_targets = []

    for block in blocks:
        lines = block["lines"]
        trans_refs = [_TRANS_REF_RE.search(l).group(1)
                      for l in lines if _TRANS_REF_RE.search(l)]

        if trans_refs and not block["ref"]:
            pending_targets.extend(trans_refs)
        elif block["ref"]:
            source_ref = block["ref"].lstrip("^")
            pending_targets.extend(trans_refs)
            for target_ref in pending_targets:
                pair = (source_ref, target_ref)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    alignments.append({
                        "source_segment_reference": source_ref,
                        "target_segment_reference": target_ref,
                    })
            pending_targets = []

    out = {"alignments": alignments}
    out_path = _out_path(source_path.stem, "alignment")
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path, out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    args = (argv if argv is not None else sys.argv[1:])
    usage = (
        'Usage:\n'
        '  python3 4-SYSTEM\\scripts\\parser-root-text\\parser.py '
        '"<source.md>" "<file.lint.json>"'
    )

    if len(args) != 2:
        print(usage)
        sys.exit(0 if not args else 1)

    source_path, lint_path = Path(args[0]), Path(args[1])
    if source_path.suffix != ".md" or ".lint" not in lint_path.name:
        print(usage)
        sys.exit(1)

    had_error = False

    try:
        source_fm, _ = _read_source(source_path)
        source_file_type = source_fm.get("file_type", "")
    except Exception as exc:
        print(f"ERROR reading source: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        text_out = extract_text_input(lint_path, source_path.stem)
        print(f"OK    {lint_path}  ->  {text_out}")
    except Exception as exc:
        print(f"ERROR text_input: {exc}", file=sys.stderr)
        had_error = True

    edition_result = None
    try:
        edition_out, edition_result = build_edition(source_path, lint_path)
        segs = edition_result["segmentation"]["segments"]
        content_len = len(edition_result["content"])
        by_type = {}
        for s in segs:
            by_type[s["type"]] = by_type.get(s["type"], 0) + 1
        print(f"OK    {source_path}  ->  {edition_out}")
        print(f"  content length   : {content_len} chars")
        print(f"  segments         : {len(segs)}")
        for t, n in sorted(by_type.items()):
            print(f"    {t}: {n}")
        n_head = len(edition_result.get("headings") or [])
        print(f"  headings (TOC)   : {n_head}")
    except Exception as exc:
        print(f"ERROR edition: {exc}", file=sys.stderr)
        had_error = True

    if edition_result is not None:
        try:
            toc_out, toc_result = build_toc(source_path, edition_result)
            sections = toc_result["sections"]
            total_sub = sum(len(s.get("subsections", [])) for s in sections)
            print(f"OK    {source_path}  ->  {toc_out}")
            print(f"  sections         : {len(sections)}")
            print(f"  subsections      : {total_sub}")
        except Exception as exc:
            print(f"ERROR toc: {exc}", file=sys.stderr)
            had_error = True

    if source_file_type in ("translation", "commentary"):
        try:
            align_out, align_result = build_alignment(source_path)
            n = len(align_result["alignments"])
            print(f"OK    {source_path}  ->  {align_out}")
            print(f"  alignments       : {n}")
        except Exception as exc:
            print(f"ERROR alignment: {exc}", file=sys.stderr)
            had_error = True

    if had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
