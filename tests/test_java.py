"""Java SDK tests — layout + HTTP; javac smoke when JDK present."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .common import REPO, base_url, load_api_key, run_lang, skip_native


def _native() -> list[str]:
    javac = shutil.which("javac")
    java = shutil.which("java")
    if not javac or not java:
        return skip_native("java", "jdk not installed")
    src = REPO / "java" / "src" / "main" / "java" / "org" / "indox" / "IndoxClient.java"
    key = load_api_key()
    base = base_url()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        print("[java] compile IndoxClient")
        proc = subprocess.run(
            [javac, "-d", str(out), str(src)],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return [f"javac: {proc.stderr.strip() or proc.returncode}"]
        runner = out / "Smoke.java"
        runner.write_text(
            """
public class Smoke {
  public static void main(String[] args) throws Exception {
    org.indox.IndoxClient c = org.indox.IndoxClient.fromEnv();
    java.net.http.HttpClient http = java.net.http.HttpClient.newHttpClient();
    java.net.http.HttpRequest req = java.net.http.HttpRequest.newBuilder()
      .uri(java.net.URI.create(c.getBaseUrl() + "/api/v1/health/"))
      .header("Authorization", c.authorizationHeader())
      .header("Accept", "application/json")
      .GET().build();
    java.net.http.HttpResponse<String> res = http.send(req,
      java.net.http.HttpResponse.BodyHandlers.ofString());
    int code = res.statusCode();
    if (code >= 500) throw new RuntimeException("health HTTP " + code);
    System.out.println("PASS java IndoxClient health HTTP " + code);
  }
}
""".strip(),
            encoding="utf-8",
        )
        proc = subprocess.run([javac, "-cp", str(out), str(runner)], check=False, capture_output=True, text=True)
        if proc.returncode != 0:
            return [f"javac Smoke: {proc.stderr.strip() or proc.returncode}"]
        env = os.environ.copy()
        env["INDOX_API_KEY"] = key
        env["INDOX_BASE_URL"] = base
        proc = subprocess.run(
            [java, "-cp", str(out), "Smoke"],
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.stdout:
            print(proc.stdout.rstrip())
        if proc.returncode != 0:
            return [f"java native: {proc.stderr.strip() or proc.returncode}"]
    return []


def test_java() -> list[str]:
    return run_lang("java", native=_native)


if __name__ == "__main__":
    raise SystemExit(1 if test_java() else 0)
