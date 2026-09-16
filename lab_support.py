"""File handling and checks for Lab 04. The retrieval exercises live in the notebook."""
from collections import Counter
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
CHECKS = {}


def check(label, test, requires=()):
    """Distinguish an unfinished exercise from an incorrect implementation."""
    missing = [name for name in requires if CHECKS.get(name) != "PASS"]
    if missing:
        CHECKS[label] = "BLOCKED"
        print(f"{label}: BLOCKED — first complete {', '.join(missing)}.")
        return False
    try:
        test()
    except NotImplementedError as exc:
        CHECKS[label] = "INCOMPLETE"
        print(f"{label}: INCOMPLETE — {exc}")
        return False
    except Exception:
        CHECKS[label] = "FAIL"
        raise
    CHECKS[label] = "PASS"
    print(f"{label}: PASS")
    return True


def ready(*labels):
    missing = [name for name in labels if CHECKS.get(name) != "PASS"]
    if missing:
        print("Not run: first complete " + ", ".join(missing) + ".")
        return False
    return True


def manifest_records(collection="docs_collection"):
    if collection not in {"docs_collection", "test_collection"}:
        raise ValueError("Use docs_collection or test_collection.")
    payload = json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))
    return sorted((row for row in payload["records"] if row["collection"] == collection),
                  key=lambda row: row["file"])


def snapshot_bytes(row):
    path = (ROOT / "data" / row["file"]).resolve()
    path.relative_to((ROOT / "data").resolve())
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != row["sha256"]:
        raise ValueError(f"Snapshot checksum mismatch: {row['file']}")
    return content


def validate_index(indexer):
    """Validate the representation, including per-document token accounting."""
    lengths, urls, index = indexer.doc_lengths, indexer.doc_urls, indexer.index
    assert set(lengths) == set(urls), "Document dictionaries disagree."
    assert all(type(d) is int and d >= 0 for d in lengths), "Invalid document ID."
    assert all(type(n) is int and n > 0 for n in lengths.values()), "Empty documents must be skipped."
    totals = Counter()
    for term, entry in index.items():
        assert isinstance(term, str) and term, "Invalid term."
        assert isinstance(entry, list) and len(entry) >= 2, "Term has no postings."
        cf, postings = entry[0], entry[1:]
        assert type(cf) is int and cf > 0, "Invalid collection frequency."
        ids = [d for d, tf in postings]
        assert ids == sorted(set(ids)), "Postings must have unique, ascending IDs."
        assert cf == sum(tf for d, tf in postings), "Collection frequency mismatch."
        for d, tf in postings:
            assert d in lengths, "Posting references an unknown document."
            assert type(tf) is int and 0 < tf <= lengths[d], "Invalid term frequency."
            totals[d] += tf
    assert dict(totals) == lengths, "Postings do not account for each document's length."
    assert sum(v[0] for v in index.values()) == sum(lengths.values()), "Token total mismatch."
    return True


def _write_json(path, payload):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def save_index(indexer, folder):
    """Store three readable dictionaries and a configuration/checksum manifest."""
    validate_index(indexer)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    payloads = {"index.json": indexer.index, "doc_urls.json": indexer.doc_urls,
                "doc_lengths.json": indexer.doc_lengths}
    hashes = {}
    for name, payload in payloads.items():
        _write_json(folder / name, payload)
        hashes[name] = hashlib.sha256((folder / name).read_bytes()).hexdigest()
    _write_json(folder / "metadata.json", {
        "schema_version": 1, "preprocessing": indexer.prep.config(), "sha256": hashes
    })


def load_index(factory, folder):
    """Restore integer document IDs and tuple postings lost in JSON encoding."""
    folder = Path(folder)
    metadata = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
    obj = factory()
    if metadata.get("schema_version") != 1 or metadata.get("preprocessing") != obj.prep.config():
        raise ValueError("Index schema or preprocessing configuration does not match.")
    values = {}
    for name in ["index.json", "doc_urls.json", "doc_lengths.json"]:
        raw = (folder / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != metadata["sha256"].get(name):
            raise ValueError(f"Saved index checksum mismatch: {name}")
        values[name] = json.loads(raw)
    obj.doc_urls = {int(d): url for d, url in values["doc_urls.json"].items()}
    obj.doc_lengths = {int(d): n for d, n in values["doc_lengths.json"].items()}
    obj.index = {term: [entry[0], *[tuple(p) for p in entry[1:]]]
                 for term, entry in values["index.json"].items()}
    obj._last_doc_id = max(obj.doc_urls, default=-1)
    validate_index(obj)
    return obj


def persist_page(content, url, folder):
    """Use a fixed-length filename, with the original URL in a sidecar file."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    path = folder / f"{digest}.html"
    path.write_bytes(content)
    _write_json(folder / f"{digest}.json", {"url": url, "file": path.name})
    return path
