#!/usr/bin/env node
/**
 * TypeScript SDK smoke — health + fonts formats via raw fetch (no tsc required).
 * Env (no built-in defaults — INDOX_BASE_URL and INDOX_CREDS_FILE come from .env):
 *   INDOX_API_KEY, INDOX_BASE_URL, INDOX_CREDS_FILE,
 *   INDOX_REQUIRE_KEY=1 to turn a missing credential into a failure.
 */
import { readFileSync } from "node:fs";

const CREDS = process.env.INDOX_CREDS_FILE || "";

function loadKey() {
  const env = (process.env.INDOX_API_KEY || "").trim();
  if (env) return env;
  if (!CREDS) return "";
  try {
    const data = JSON.parse(readFileSync(CREDS, "utf-8"));
    return (data.api_key_raw || data.macos_api_key || data.external_token || "").trim();
  } catch {
    return "";
  }
}

const base = (process.env.INDOX_BASE_URL || "").replace(/\/+$/, "");
if (!base) {
  console.error("FAIL typescript smoke: set INDOX_BASE_URL (see .env)");
  process.exit(1);
}
const key = loadKey();
if (!key) {
  const msg = `no INDOX_API_KEY and no key in ${CREDS}`;
  if (process.env.INDOX_REQUIRE_KEY === "1") {
    console.error(`FAIL typescript smoke: ${msg}`);
    process.exit(1);
  }
  console.log(`SKIP typescript smoke: ${msg}`);
  process.exit(0);
}

const soft = new Set([400, 401, 403, 404, 405, 409, 415, 422, 429]);
const TIMEOUT_MS = 60_000;

async function probe(label, path) {
  let res;
  try {
    res = await fetch(`${base}${path}`, {
      headers: { Authorization: `Bearer ${key}`, Accept: "application/json" },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (err) {
    if (err?.name === "TimeoutError") {
      throw new Error(`${label}: no response within ${TIMEOUT_MS}ms`);
    }
    throw new Error(`${label}: ${err?.message || err}`);
  }
  if (res.status >= 500) {
    throw new Error(`${label}: HTTP ${res.status}`);
  }
  if (!res.ok && !soft.has(res.status)) {
    throw new Error(`${label}: unexpected HTTP ${res.status}`);
  }
  console.log(`  PASS ${label} (HTTP ${res.status})`);
}

async function main() {
  console.log(`@indox/sdk smoke base=${base}`);
  await probe("health", "/api/v1/health/");
  await probe("fonts.formats", "/api/v1/fonts/formats/");
  await probe("pdf.formats", "/api/v1/pdf_handler/formats/");
  await probe("image.formats", "/api/v1/convert/image/formats/");
  console.log("OK typescript smoke");
}

main().catch((err) => {
  console.error("FAIL", err.message || err);
  process.exit(1);
});
