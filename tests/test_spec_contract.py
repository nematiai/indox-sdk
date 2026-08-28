"""Shape gates the drift check cannot make — it compares paths, never bodies.

Each assertion here corresponds to a defect that shipped in indox-client 0.4.0 and
that `make drift` reported green throughout:

  * upload fields typed as bare strings, so no generated client could send a file
  * ``DocumentConversionAccepted`` still modelling ``job_id`` after the server
    renamed it to ``id``, which broke PDF convert in 7 of 8 languages
  * the ADV signing group under-expanding, so two real routes reached no client

Run: python3 -m pytest tests/test_spec_contract.py
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPEC = json.loads((REPO / "spec" / "openapi-public.json").read_text(encoding="utf-8"))
SCHEMAS = SPEC["components"]["schemas"]

# The DRF convert bodies — the only ones that take a real file upload.
UPLOAD_SCHEMAS = ("ImageConvert", "VideoConvert", "ModelConvert")


def test_upload_fields_are_binary():
    """Without format: binary the generators emit `file: string` and cannot upload."""
    for name in UPLOAD_SCHEMAS:
        prop = SCHEMAS[name]["properties"]["file"]
        assert prop.get("format") == "binary", f"{name}.file is {prop.get('format')!r}"
        assert prop.get("type") == "string", f"{name}.file type is {prop.get('type')!r}"


def test_document_conversion_accepted_matches_the_wire():
    """The 202 body of POST /pdf_handler/convert/ — `id`, never `job_id`."""
    schema = SCHEMAS["DocumentConversionAccepted"]
    props = schema.get("properties") or {}
    assert "id" in props, "conversion id missing — callers cannot poll or download"
    assert "job_id" not in props, "job_id was renamed to id server-side; the spec is stale"
    assert "service" in props, "server sends `service`; regenerate the spec"


def test_adv_signing_group_is_fully_expanded():
    """An under-populated ellipsis group raises nothing, so assert the count."""
    signing = [p for p in SPEC["paths"] if "/signing/" in p]
    assert len(signing) == 6, f"expected 6 signing paths, found {len(signing)}: {signing}"
    for suffix in ("certificate/", "wet-signature/"):
        assert any(p.endswith(suffix) for p in signing), f"missing signing route: {suffix}"


def test_no_synthesized_stubs():
    assert not SPEC.get("x-indox-synthesized-ops"), "spec contains synthesized stub ops"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all spec contract checks passed")
