"""Live convert coverage for fonts / pdf / image / video / model.

Inventory: every format + route the API advertises.
Convert: for each sample file under colab/<service>/samples/, convert to
every output the API allows for that input format.

Usage (repo root):
  PYTHONPATH=. python3 -m tests.convert_coverage
  PYTHONPATH=. python3 -m tests.convert_coverage --service pdf
  PYTHONPATH=. python3 -m tests.convert_coverage --inventory-only
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
import uuid
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.creds import load_api_key  # noqa: E402
from tools.env import get_env  # noqa: E402

COLAB = REPO / "colab"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

SERVICES: dict[str, dict[str, Any]] = {
    "fonts": {
        "formats_path": "/api/v1/fonts/formats/",
        "ops_path": None,
        "kind": "fonts",
        "samples": COLAB / "fonts" / "samples",
        "ext_to_fmt": {
            ".ttf": "ttf",
            ".otf": "otf",
            ".woff": "woff",
            ".woff2": "woff2",
            ".eot": "eot",
            ".svg": "svg",
            ".ttc": "ttc",
            ".pfb": "pfb",
            ".pfa": "pfa",
        },
    },
    "pdf": {
        "formats_path": "/api/v1/pdf_handler/formats/",
        "ops_path": None,
        "kind": "multipart",
        "convert_path": "/api/v1/pdf_handler/convert/",
        "status_tmpl": "/api/v1/pdf_handler/conversion/{id}/",
        "samples": COLAB / "pdf" / "samples",
        "ext_to_fmt": {
            ".txt": "txt",
            ".md": "md",
            ".html": "html",
            ".htm": "html",
            ".docx": "docx",
            ".odt": "odt",
            ".rtf": "rtf",
            ".epub": "epub",
            ".csv": "csv",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yml",
            ".pdf": "pdf",
        },
    },
    "image": {
        "formats_path": "/api/v1/convert/image/formats/",
        "ops_path": "/api/v1/convert/image/operations/",
        "kind": "multipart",
        "convert_path": "/api/v1/convert/image/convert/",
        "status_tmpl": "/api/v1/convert/image/conversion/{id}/",
        "samples": COLAB / "image" / "samples",
        "ext_to_fmt": {
            ".png": "png",
            ".jpg": "jpg",
            ".jpeg": "jpeg",
            ".webp": "webp",
            ".gif": "gif",
            ".bmp": "bmp",
            ".tif": "tif",
            ".tiff": "tiff",
            ".svg": "svg",
            ".heic": "heic",
            ".pdf": "pdf",
        },
    },
    "video": {
        "formats_path": "/api/v1/convert/video/formats/",
        "ops_path": None,
        "kind": "multipart",
        "convert_path": "/api/v1/convert/video/convert/",
        "status_tmpl": "/api/v1/media_core/conversion/{id}/",
        "samples": COLAB / "video" / "samples",
        "ext_to_fmt": {
            ".mp4": "mp4",
            ".mov": "mov",
            ".mkv": "mkv",
            ".webm": "webm",
            ".avi": "avi",
            ".mp3": "mp3",
            ".wav": "wav",
            ".flac": "flac",
            ".m4a": "m4a",
            ".ogg": "ogg",
        },
    },
    "model": {
        "formats_path": "/api/v1/convert/model/formats/",
        "ops_path": "/api/v1/convert/model/operations/",
        "kind": "multipart",
        "convert_path": "/api/v1/convert/model/convert/",
        "status_tmpl": "/api/v1/convert/model/conversion/{id}/",
        "samples": COLAB / "model" / "samples",
        "ext_to_fmt": {
            ".obj": "obj",
            ".stl": "stl",
            ".glb": "glb",
            ".gltf": "gltf",
            ".fbx": "fbx",
            ".ply": "ply",
            ".dae": "dae",
            ".3ds": "3ds",
            ".blend": "blend",
        },
    },
}


@dataclass
class Route:
    service: str
    input_format: str
    output_format: str
    engine: str | None = None


@dataclass
class Inventory:
    service: str
    formats: int | None
    routes: int | None
    inputs: list[str]
    outputs: list[str]
    route_list: list[Route] = field(default_factory=list)
    operations: int | None = None


@dataclass
class JobResult:
    service: str
    file: str
    input_format: str
    output_format: str
    ok: bool
    detail: str
    id: str = ""
    seconds: float = 0.0


class Api:
    def __init__(self, base_url: str, api_key: str, *, timeout: float = 60.0) -> None:
        self.base = base_url.rstrip("/")
        self.key = api_key
        self.timeout = timeout

    def _headers(self, content_type: str | None = None) -> dict[str, str]:
        h = {
            "Authorization": f"Bearer {self.key}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if content_type:
            h["Content-Type"] = content_type
        return h

    def json(
        self, method: str, path: str, *, data: bytes | None = None, content_type: str | None = None
    ) -> tuple[int, Any]:
        url = path if path.startswith("http") else self.base + path
        req = urllib.request.Request(
            url, data=data, method=method, headers=self._headers(content_type)
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
                raw = resp.read()
                body = json.loads(raw.decode() or "null") if raw else None
                return int(resp.status), body
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                body = json.loads(raw.decode() or "null")
            except Exception:
                body = raw.decode(errors="replace")[:800]
            return int(exc.code), body

    def multipart(self, path: str, fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]):
        boundary = f"----IndoxBoundary{uuid.uuid4().hex}"
        chunks: list[bytes] = []
        for name, value in fields.items():
            chunks.append(
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
            )
        for name, (fname, blob, ctype) in files.items():
            chunks.append(
                (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{name}"; filename="{fname}"\r\n'
                    f"Content-Type: {ctype}\r\n\r\n"
                ).encode()
                + blob
                + b"\r\n"
            )
        chunks.append(f"--{boundary}--\r\n".encode())
        return self.json(
            "POST",
            path,
            data=b"".join(chunks),
            content_type=f"multipart/form-data; boundary={boundary}",
        )


def _routes_from_engines(service: str, data: dict[str, Any]) -> list[Route]:
    out: list[Route] = []
    seen: set[tuple[str, str, str | None]] = set()
    for engine, meta in (data.get("engines") or {}).items():
        for inp in meta.get("inputs") or []:
            for outp in meta.get("outputs") or []:
                key = (str(inp).lower(), str(outp).lower(), engine)
                if key in seen:
                    continue
                seen.add(key)
                out.append(
                    Route(service, str(inp).lower(), str(outp).lower(), engine=engine)
                )
    return out


def _routes_from_operations(service: str, data: dict[str, Any]) -> list[Route]:
    out: list[Route] = []
    seen: set[tuple[str, str]] = set()
    for row in data.get("data") or []:
        inp = str(row.get("input_format") or "").lower()
        outp = str(row.get("output_format") or "").lower()
        if not inp or not outp:
            continue
        if (inp, outp) in seen:
            continue
        seen.add((inp, outp))
        out.append(
            Route(service, inp, outp, engine=str(row.get("engine") or "") or None)
        )
    return out


def fetch_inventory(api: Api, service: str) -> Inventory:
    cfg = SERVICES[service]
    code, data = api.json("GET", cfg["formats_path"])
    if code != 200 or not isinstance(data, dict):
        raise RuntimeError(f"{service} formats HTTP {code}: {data}")

    route_list: list[Route] = []
    operations = None

    if cfg.get("ops_path"):
        oc, od = api.json("GET", cfg["ops_path"])
        if oc == 200 and isinstance(od, dict):
            route_list = _routes_from_operations(service, od)
            operations = len(od.get("data") or [])

    if "engines" in data:
        inputs: set[str] = set()
        outputs: set[str] = set()
        for meta in (data.get("engines") or {}).values():
            inputs.update(str(x).lower() for x in (meta.get("inputs") or []))
            outputs.update(str(x).lower() for x in (meta.get("outputs") or []))
        if not route_list:
            route_list = _routes_from_engines(service, data)
        # Prefer API-reported total_routes when present (deduped / authoritative).
        routes = data.get("total_routes")
        if routes is None:
            routes = len({(r.input_format, r.output_format) for r in route_list})
        return Inventory(
            service=service,
            formats=data.get("total_formats"),
            routes=int(routes),
            inputs=sorted(inputs),
            outputs=sorted(outputs),
            route_list=route_list,
            operations=operations,
        )

    inputs_l = [str(x).lower() for x in (data.get("input_formats") or [])]
    outputs_l = [str(x).lower() for x in (data.get("output_formats") or [])]
    if not route_list:
        # model formats without ops fallback: full cartesian (over-approx)
        route_list = [
            Route(service, i, o)
            for i in inputs_l
            for o in outputs_l
        ]
    routes = operations if operations is not None else len(
        {(r.input_format, r.output_format) for r in route_list}
    )
    return Inventory(
        service=service,
        formats=len(set(inputs_l) | set(outputs_l)),
        routes=int(routes),
        inputs=inputs_l,
        outputs=outputs_l,
        route_list=route_list,
        operations=operations,
    )


def outputs_for_input(inv: Inventory, input_format: str) -> list[str]:
    fmt = input_format.lower()
    outs = sorted({r.output_format for r in inv.route_list if r.input_format == fmt})
    if outs:
        return outs
    # fonts: query /formats/{input}/ when route_list may be incomplete
    return sorted(inv.outputs)


def list_samples(service: str) -> list[tuple[Path, str]]:
    cfg = SERVICES[service]
    root: Path = cfg["samples"]
    ext_map: dict[str, str] = cfg["ext_to_fmt"]
    if not root.is_dir():
        return []
    found: list[tuple[Path, str]] = []
    for path in sorted(root.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        fmt = ext_map.get(path.suffix.lower())
        if fmt:
            found.append((path, fmt))
    return found


def job_id(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    return str(payload.get("id") or payload.get("conversion_id") or "")


def wait_conversion(
    api: Api, status_tmpl: str, conversion_id: str, *, timeout: float, poll: float
) -> dict[str, Any]:
    start = time.time()
    last: Any = None
    while True:
        code, last = api.json("GET", status_tmpl.format(id=conversion_id))
        if code >= 500:
            raise RuntimeError(f"status HTTP {code}: {last}")
        if isinstance(last, dict):
            state = str(last.get("status") or "").lower()
            if state in {"completed", "success"}:
                return last
            if state in {"failed", "error"}:
                raise RuntimeError(
                    str(
                        last.get("error")
                        or last.get("error_message")
                        or last.get("detail")
                        or last
                    )
                )
        if time.time() - start > timeout:
            raise TimeoutError(f"timed out after {timeout}s; last={last!r}")
        time.sleep(poll)


def convert_one(
    api: Api,
    service: str,
    path: Path,
    input_format: str,
    output_format: str,
    *,
    poll_timeout: float,
    poll_interval: float,
) -> JobResult:
    cfg = SERVICES[service]
    t0 = time.time()
    row = JobResult(
        service=service,
        file=path.name,
        input_format=input_format,
        output_format=output_format,
        ok=False,
        detail="",
    )
    try:
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        blob = path.read_bytes()
        if cfg["kind"] == "fonts":
            code, up = api.multipart(
                "/api/v1/fonts/upload/", {}, {"file": (path.name, blob, ctype)}
            )
            if code >= 400:
                raise RuntimeError(f"upload HTTP {code}: {up}")
            s3_key = (up or {}).get("s3_key") if isinstance(up, dict) else None
            if not s3_key:
                raise RuntimeError(f"upload missing s3_key: {up!r}")
            code, payload = api.json(
                "POST",
                "/api/v1/fonts/convert/",
                data=json.dumps(
                    {
                        "s3_key": s3_key,
                        "target_format": output_format,
                        "filename": path.name,
                    }
                ).encode(),
                content_type="application/json",
            )
            if code >= 400:
                raise RuntimeError(f"convert HTTP {code}: {payload}")
            cid = job_id(payload)
            if not cid:
                raise RuntimeError(f"missing id: {payload!r}")
            row.id = cid
            final = wait_conversion(
                api,
                "/api/v1/fonts/conversion/{id}/",
                cid,
                timeout=poll_timeout,
                poll=poll_interval,
            )
        else:
            code, payload = api.multipart(
                cfg["convert_path"],
                {"target_formats": output_format},
                {"file": (path.name, blob, ctype)},
            )
            if code >= 400:
                raise RuntimeError(f"convert HTTP {code}: {payload}")
            cid = job_id(payload)
            if not cid:
                raise RuntimeError(f"missing id: {payload!r}")
            row.id = cid
            final = wait_conversion(
                api,
                cfg["status_tmpl"],
                cid,
                timeout=poll_timeout,
                poll=poll_interval,
            )
        row.ok = True
        row.detail = f"completed ({final.get('status')})"
    except Exception as exc:  # noqa: BLE001
        row.detail = f"{type(exc).__name__}: {exc}"
    row.seconds = round(time.time() - t0, 2)
    return row


def plan_jobs(
    inventories: dict[str, Inventory], services: Iterable[str]
) -> list[tuple[str, Path, str, str]]:
    """(service, path, input_fmt, output_fmt) for every sample × every valid output."""
    jobs: list[tuple[str, Path, str, str]] = []
    for service in services:
        inv = inventories[service]
        for path, inp in list_samples(service):
            for outp in outputs_for_input(inv, inp):
                jobs.append((service, path, inp, outp))
    return jobs


def run(
    *,
    services: list[str] | None = None,
    inventory_only: bool = False,
    base_url: str | None = None,
    api_key: str | None = None,
    poll_timeout: float = 300.0,
    poll_interval: float = 1.0,
    max_jobs: int | None = None,
) -> dict[str, Any]:
    services = services or list(SERVICES)
    for s in services:
        if s not in SERVICES:
            raise SystemExit(f"unknown service {s!r}; choose from {sorted(SERVICES)}")

    base = (
        base_url
        or os.environ.get("INDOX_BASE_URL")
        or get_env("INDOX_PUBLIC_BASE_URL")
        or get_env("INDOX_BASE_URL")
        or "https://indox.org"
    ).rstrip("/")
    # Prefer public when local base is unreachable from this host — callers can override.
    if base.startswith("http://localhost") or base.startswith("http://127.0.0.1"):
        pub = get_env("INDOX_PUBLIC_BASE_URL")
        if pub:
            base = pub.rstrip("/")

    key = (api_key or os.environ.get("INDOX_API_KEY") or "").strip() or load_api_key()
    api = Api(base, key)

    inventories: dict[str, Inventory] = {}
    print(f"Base URL: {base}")
    print("=== Inventory (all convert routes) ===")
    total_routes = 0
    total_formats = 0
    for service in services:
        inv = fetch_inventory(api, service)
        # Enrich fonts with per-input outputs from /formats/{input}/
        if service == "fonts":
            refined: list[Route] = []
            for inp in inv.inputs:
                code, body = api.json("GET", f"/api/v1/fonts/formats/{inp}/")
                if code == 200 and isinstance(body, dict):
                    outs = body.get("outputs") or body.get("formats") or []
                    if isinstance(outs, dict):
                        outs = list(outs.keys())
                    for item in outs:
                        if isinstance(item, dict):
                            outp = item.get("output") or item.get("format")
                            eng = item.get("engine")
                        else:
                            outp, eng = item, None
                        if not outp:
                            continue
                        refined.append(
                            Route("fonts", inp, str(outp).lower(), engine=str(eng) if eng else None)
                        )
            if refined:
                inv.route_list = refined
                inv.routes = len({(r.input_format, r.output_format) for r in refined})
        inventories[service] = inv
        total_routes += int(inv.routes or 0)
        total_formats += int(inv.formats or 0)
        print(
            f"  {service:6}  formats={inv.formats!s:>5}  routes={inv.routes!s:>6}  "
            f"unique_io_pairs={len({(r.input_format, r.output_format) for r in inv.route_list}):>6}  "
            f"inputs={len(inv.inputs)}  outputs={len(inv.outputs)}"
        )

    print(f"TOTAL formats={total_formats}  routes={total_routes}")

    report: dict[str, Any] = {
        "base_url": base,
        "inventory": {
            s: {
                "formats": inventories[s].formats,
                "routes": inventories[s].routes,
                "inputs": len(inventories[s].inputs),
                "outputs": len(inventories[s].outputs),
                "route_pairs": sorted(
                    {(r.input_format, r.output_format) for r in inventories[s].route_list}
                ),
            }
            for s in services
        },
        "totals": {"formats": total_formats, "routes": total_routes},
        "convert": None,
    }

    if inventory_only:
        return report

    jobs = plan_jobs(inventories, services)
    if max_jobs is not None:
        jobs = jobs[: max_jobs]

    covered_pairs = {(s, i, o) for s, _p, i, o in jobs}
    advertised = {
        (s, r.input_format, r.output_format)
        for s in services
        for r in inventories[s].route_list
    }

    print(
        f"\n=== Convert sample×all-outputs: {len(jobs)} jobs "
        f"(covers {len(covered_pairs)} / {len(advertised)} advertised pairs with current samples) ==="
    )

    try:
        from tqdm.auto import tqdm
    except Exception:  # noqa: BLE001
        tqdm = None  # type: ignore

    results: list[JobResult] = []
    iterator = tqdm(jobs, desc="convert", unit="job") if tqdm else jobs
    for service, path, inp, outp in iterator:
        row = convert_one(
            api,
            service,
            path,
            inp,
            outp,
            poll_timeout=poll_timeout,
            poll_interval=poll_interval,
        )
        results.append(row)
        mark = "PASS" if row.ok else "FAIL"
        line = f"{mark} {service} {path.name} ({inp}→{outp}) {row.detail} ({row.seconds}s)"
        if tqdm:
            iterator.set_postfix_str(f"{service} {inp}→{outp}")  # type: ignore[attr-defined]
            if not row.ok:
                iterator.write(line)  # type: ignore[attr-defined]
        else:
            print(line, flush=True)

    n_ok = sum(1 for r in results if r.ok)
    n_fail = sum(1 for r in results if not r.ok)
    print(f"\nConvert: {n_ok} PASS / {n_fail} FAIL / {len(results)} total")
    print(
        f"Route coverage with samples: {len(covered_pairs)} / {total_routes} "
        f"advertised routes ({(100 * len(covered_pairs) / total_routes) if total_routes else 0:.1f}%)"
    )

    report["convert"] = {
        "pass": n_ok,
        "fail": n_fail,
        "total": len(results),
        "covered_pairs": len(covered_pairs),
        "advertised_routes": total_routes,
        "jobs": [r.__dict__ for r in results],
    }
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--service", action="append", choices=sorted(SERVICES))
    p.add_argument("--inventory-only", action="store_true")
    p.add_argument("--base-url", default="")
    p.add_argument("--max-jobs", type=int, default=None)
    p.add_argument("--poll-timeout", type=float, default=300.0)
    p.add_argument(
        "--save-json",
        default=str(REPO / "colab" / "convert_coverage_results.json"),
    )
    args = p.parse_args(argv)

    report = run(
        services=args.service,
        inventory_only=args.inventory_only,
        base_url=args.base_url or None,
        poll_timeout=args.poll_timeout,
        max_jobs=args.max_jobs,
    )
    out = Path(args.save_json)
    # Keep route_pairs but avoid huge dumps when saving convert jobs only summary+failures
    save = dict(report)
    if save.get("convert") and isinstance(save["convert"], dict):
        jobs = save["convert"].get("jobs") or []
        save["convert"] = {
            **{k: v for k, v in save["convert"].items() if k != "jobs"},
            "failures": [j for j in jobs if not j.get("ok")],
            "passes": [j for j in jobs if j.get("ok")],
        }
    # trim route_pairs in inventory for file size — keep counts; full pairs in inventory-only
    if not args.inventory_only:
        for s, meta in (save.get("inventory") or {}).items():
            pairs = meta.get("route_pairs") or []
            meta["route_pairs_count"] = len(pairs)
            meta.pop("route_pairs", None)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(save, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out}")

    if args.inventory_only:
        return 0 if report["totals"]["routes"] > 0 else 1
    conv = report.get("convert") or {}
    return 0 if conv.get("fail", 1) == 0 and conv.get("total", 0) > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
