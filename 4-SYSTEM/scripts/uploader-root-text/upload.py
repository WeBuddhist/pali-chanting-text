#!/usr/bin/env python3
"""Upload parser payloads to the webuddhist library API.

Takes a parser output folder — ``parser-root-text/output/<stem>/`` — and posts
the payloads it contains, in order:

    1. <stem>.text.json       POST /v2/texts                                  -> id
    2. <stem>.edition.json    POST /v2/texts/{text_id}/editions               -> id
    3. <stem>.toc.json        POST /v2/editions/{edition_id}/table-of-contents -> id
    4. <stem>.alignment.json  PUT  /v2/editions/{edition_id}/alignments/{root_edition_id}
                                                                              -> 204

Returned ids are recorded in ``<stem>.ids.json`` beside the payloads and, when
the source ``.md`` can be located, patched into its YAML frontmatter as
``text_id`` / ``edition_id`` / ``toc_id``. Either record makes a second run a
no-op instead of a duplicate; ``--force`` overrides.

Step 4 runs only when the folder holds an alignment payload (translations and
commentaries). It needs the ROOT text's ``edition_id``, taken from the file
named by the source's ``root_text:`` — so upload a root text before its
translations, or pass --root-edition-id explicitly.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "https://library.webuddhist.com"
PARSER_OUTPUT = Path(__file__).resolve().parent.parent / "parser-root-text" / "output"
REPO_ROOT = PARSER_OUTPUT.parents[3]
YAML_PROPS_RE = re.compile(r"\A(---\r?\n)(.*?)(\r?\n---\r?\n?)", re.DOTALL)


# ---------------------------------------------------------------------------
# locating things
# ---------------------------------------------------------------------------

def _nfc(value):
    return unicodedata.normalize("NFC", str(value))


def _find_source_md(stem):
    """Locate <stem>.md, tolerating NFC/NFD differences in the filename."""
    wanted = _nfc(stem) + ".md"
    for root in (REPO_ROOT / "1-SOURCES", REPO_ROOT):
        if not root.is_dir():
            continue
        exact = sorted(root.rglob(stem + ".md"))
        if exact:
            return exact[0]
        for cand in sorted(root.rglob("*.md")):
            if _nfc(cand.name) == wanted:
                return cand
    return None


def resolve_input(arg):
    """Accept a payload folder, a source .md, or a bare stem.

    Returns (payload_dir, stem, source_md_or_None).
    """
    path = Path(arg)

    if path.is_dir():
        payload_dir, stem = path, path.name
    elif path.suffix == ".md":
        if not path.exists():
            raise SystemExit(f"ERROR {path}: file not found")
        return PARSER_OUTPUT / path.stem, path.stem, path
    else:
        candidate = PARSER_OUTPUT / str(arg)
        if not candidate.is_dir():
            raise SystemExit(
                f"ERROR {arg}: not a payload folder, a .md file, or a stem under\n"
                f"      {PARSER_OUTPUT}"
            )
        payload_dir, stem = candidate, candidate.name

    return payload_dir, stem, _find_source_md(stem)


def _load_payload(payload_dir, stem, kind, required=True):
    path = payload_dir / f"{stem}.{kind}.json"
    if not path.exists():
        if required:
            raise SystemExit(
                f"ERROR missing payload {path}\n"
                f"      run the parser for {stem} first"
            )
        return None, path
    return json.loads(path.read_text(encoding="utf-8")), path


# ---------------------------------------------------------------------------
# id bookkeeping
# ---------------------------------------------------------------------------

ID_KEYS = ("text_id", "edition_id", "toc_id")


def _read_frontmatter(path):
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("PyYAML is required: pip install pyyaml") from exc
    m = YAML_PROPS_RE.match(path.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit(f"ERROR {path}: no YAML frontmatter found")
    return yaml.safe_load(m.group(2)) or {}


def _patch_frontmatter(path, updates):
    """Set frontmatter keys in place, preserving the file's line endings."""
    updates = {k: v for k, v in updates.items() if v}
    if not updates:
        return []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    m = YAML_PROPS_RE.match(text)
    if not m:
        return []
    head, block, tail = m.group(1), m.group(2), m.group(3)
    eol = "\r\n" if "\r\n" in text else "\n"
    changed = []
    for key, value in updates.items():
        # [^\r\n] rather than . so a CRLF file keeps its \r — matching on
        # ".*$" swallows the \r and silently rewrites that line to LF.
        pattern = re.compile(r"^(%s:)[ \t]*([^\r\n]*)" % re.escape(key), re.MULTILINE)
        found = pattern.search(block)
        if found:
            if found.group(2).strip() == str(value):
                continue
            block = pattern.sub(lambda _m, k=key, v=value: "%s: %s" % (k, v), block, count=1)
        else:
            block = block + eol + "%s: %s" % (key, value)
        changed.append(key)
    if not changed:
        return []
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(head + block + tail + text[m.end():])
    return changed


def _ids_path(payload_dir, stem):
    return payload_dir / f"{stem}.ids.json"


def _load_known_ids(payload_dir, stem, source_md):
    """Ids already assigned: the source .md wins, the sidecar is the fallback."""
    ids = {}
    sidecar = _ids_path(payload_dir, stem)
    if sidecar.exists():
        try:
            data = json.loads(sidecar.read_text(encoding="utf-8"))
        except ValueError:
            data = {}
        for key in ID_KEYS:
            val = str(data.get(key) or "").strip()
            if val:
                ids[key] = val
    if source_md is not None:
        fm = _read_frontmatter(source_md)
        for key in ID_KEYS:
            val = str(fm.get(key) or "").strip()
            if val:
                ids[key] = val
    return ids


def _save_ids(payload_dir, stem, source_md, result):
    sidecar = _ids_path(payload_dir, stem)
    sidecar.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  WROTE {sidecar.name}")
    if source_md is not None:
        changed = _patch_frontmatter(
            source_md, {k: result.get(k) for k in ID_KEYS}
        )
        if changed:
            print(f"  PATCHED {source_md.name}: {', '.join(changed)}")


def _resolve_path_near(val, source_path):
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


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def _request(method, url, payload, api_key, dry_run=False):
    """Returns (status, parsed_body_or_None). Exits on any HTTP/network error."""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if dry_run:
        print(f"  DRY-RUN {method} {url}  ({len(body)} bytes)")
        return 0, None

    headers = {"Content-Type": "application/json", "accept": "*/*"}
    if api_key:
        headers["X-API-Key"] = api_key

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            status, raw = resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(
            f"ERROR {method} {url}\n"
            f"      HTTP {exc.code} {exc.reason}\n"
            f"      {detail[:2000]}"
        )
    except urllib.error.URLError as exc:
        raise SystemExit(f"ERROR {method} {url}\n      {exc.reason}")

    if not raw.strip():
        return status, None
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, {"_raw": raw}


def _extract_id(data, *names):
    if not isinstance(data, dict):
        return None
    for key in ("id", *names, "_id"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    inner = data.get("data")
    if isinstance(inner, dict):
        return _extract_id(inner, *names)
    return None


# ---------------------------------------------------------------------------
# upload one payload folder
# ---------------------------------------------------------------------------

def upload(payload_dir, stem, source_md, base_url, api_key, dry_run=False,
           force=False, skip_alignment=False, root_edition_id=None):
    if not payload_dir.is_dir():
        raise SystemExit(
            f"ERROR no payload folder {payload_dir}\n"
            f"      run the parser for {stem} first"
        )

    print(f"\n=== {stem} ===")
    print(f"    payloads: {payload_dir}")
    print(f"    source  : {source_md if source_md else '(not found — ids go to the sidecar only)'}")

    known = {} if force else _load_known_ids(payload_dir, stem, source_md)
    text_id = known.get("text_id")
    edition_id = known.get("edition_id")
    toc_id = known.get("toc_id")
    alignment_target = None

    # -- 1. text -----------------------------------------------------------
    if text_id:
        print(f"  SKIP  text        already registered: {text_id}")
    else:
        payload, path = _load_payload(payload_dir, stem, "text")
        print(f"  POST  text        <- {path.name}")
        status, data = _request("POST", f"{base_url}/v2/texts", payload, api_key, dry_run)
        if dry_run:
            text_id = "<new text_id>"
        else:
            text_id = _extract_id(data, "text_id")
            if not text_id:
                raise SystemExit(f"ERROR no id in response (HTTP {status}): {data!r}")
            print(f"        HTTP {status}  text_id = {text_id}")

    # -- 2. edition --------------------------------------------------------
    if edition_id:
        print(f"  SKIP  edition     already registered: {edition_id}")
    else:
        payload, path = _load_payload(payload_dir, stem, "edition")
        print(f"  POST  edition     <- {path.name}")
        status, data = _request(
            "POST", f"{base_url}/v2/texts/{text_id}/editions", payload, api_key, dry_run
        )
        if dry_run:
            edition_id = "<new edition_id>"
        else:
            edition_id = _extract_id(data, "edition_id")
            if not edition_id:
                raise SystemExit(f"ERROR no id in response (HTTP {status}): {data!r}")
            print(f"        HTTP {status}  edition_id = {edition_id}")

    # -- 3. table of contents ---------------------------------------------
    if toc_id:
        print(f"  SKIP  toc         already registered: {toc_id}")
    else:
        payload, path = _load_payload(payload_dir, stem, "toc")
        print(f"  POST  toc         <- {path.name}")
        status, data = _request(
            "POST", f"{base_url}/v2/editions/{edition_id}/table-of-contents",
            payload, api_key, dry_run,
        )
        if dry_run:
            toc_id = "<new toc_id>"
        else:
            toc_id = _extract_id(data, "toc_id")
            if not toc_id:
                raise SystemExit(f"ERROR no id in response (HTTP {status}): {data!r}")
            print(f"        HTTP {status}  toc_id = {toc_id}")

    # -- 4. alignment ------------------------------------------------------
    payload, align_path = _load_payload(payload_dir, stem, "alignment", required=False)
    if skip_alignment:
        print("  SKIP  alignment   --skip-alignment")
    elif payload is None:
        print(f"  SKIP  alignment   no {align_path.name} (root text — nothing to align)")
    else:
        target = root_edition_id
        if not target and source_md is not None:
            root_val = _read_frontmatter(source_md).get("root_text")
            if not root_val:
                print("  WARN  alignment   no root_text in frontmatter — skipped")
            else:
                root_path = _resolve_path_near(str(root_val), source_md)
                if root_path is None:
                    print(f"  WARN  alignment   root_text {root_val!r} not found — skipped")
                else:
                    target = str(_read_frontmatter(root_path).get("edition_id") or "").strip() or None
                    if not target:
                        print(
                            f"  WARN  alignment   {root_path.name} has no edition_id — "
                            f"upload the root text first, then re-run — skipped"
                        )
        elif not target:
            print("  WARN  alignment   source .md not found; pass --root-edition-id — skipped")

        if target:
            print(f"  PUT   alignment   <- {align_path.name}  (target {target})")
            status, _ = _request(
                "PUT", f"{base_url}/v2/editions/{edition_id}/alignments/{target}",
                payload, api_key, dry_run,
            )
            if not dry_run:
                alignment_target = target
                print(f"        HTTP {status}  ({len(payload['alignments'])} alignments)")
            else:
                alignment_target = target

    result = {
        "stem": stem,
        "source": str(source_md) if source_md else None,
        "text_id": text_id,
        "edition_id": edition_id,
        "toc_id": toc_id,
        "alignment_target_edition_id": alignment_target,
    }
    if not dry_run:
        _save_ids(payload_dir, stem, source_md, result)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Upload parser payloads to the webuddhist library API.",
        epilog='e.g. upload.py "4-SYSTEM\\scripts\\parser-root-text\\output\\तिसरण–पञ्चशील_hi"',
    )
    ap.add_argument("inputs", nargs="+",
                    help="parser output folder(s) — a source .md or a bare stem also works")
    ap.add_argument("--base-url", default=os.environ.get("WEBUDDHIST_BASE_URL", DEFAULT_BASE_URL))
    ap.add_argument("--api-key", default=os.environ.get("WEBUDDHIST_API_KEY", ""),
                    help="sent as X-API-Key (or set WEBUDDHIST_API_KEY)")
    ap.add_argument("--dry-run", action="store_true", help="show the calls without sending them")
    ap.add_argument("--force", action="store_true",
                    help="create new records even when ids are already recorded")
    ap.add_argument("--skip-alignment", action="store_true")
    ap.add_argument("--root-edition-id", default=None,
                    help="root text's edition_id for step 4, when the source .md is unavailable")
    args = ap.parse_args(argv)

    base_url = args.base_url.rstrip("/")
    results = []
    for raw in args.inputs:
        payload_dir, stem, source_md = resolve_input(raw)
        results.append(upload(
            payload_dir, stem, source_md, base_url, args.api_key,
            dry_run=args.dry_run, force=args.force,
            skip_alignment=args.skip_alignment,
            root_edition_id=args.root_edition_id,
        ))

    print("\n" + "=" * 62)
    for r in results:
        print(f"  {r['stem']}")
        print(f"    text_id     : {r['text_id'] or '-'}")
        print(f"    edition_id  : {r['edition_id'] or '-'}")
        print(f"    toc_id      : {r['toc_id'] or '-'}")
        if r["alignment_target_edition_id"]:
            print(f"    alignment   : {r['edition_id']} -> {r['alignment_target_edition_id']}"
                  f"  (HTTP 204, no id returned)")
        else:
            print("    alignment   : -")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
