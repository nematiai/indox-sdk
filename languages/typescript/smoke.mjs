#!/usr/bin/env node
/**
 * TypeScript SDK smoke — drives the hand-written client in src/client.ts.
 * That client is TypeScript, so tests/ts_build.py compiles it first and hands
 * the emitted CommonJS entry point over in INDOX_TS_CLIENT.
 * Env (no built-in defaults — INDOX_BASE_URL and INDOX_CREDS_FILE come from .env):
 *   INDOX_API_KEY, INDOX_BASE_URL, INDOX_CREDS_FILE, INDOX_TS_CLIENT,
 *   INDOX_REQUIRE_KEY=1 to turn a missing credential into a failure.
 */
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";

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
const clientPath = process.env.INDOX_TS_CLIENT || "";
if (!clientPath) {
  console.error("FAIL typescript smoke: set INDOX_TS_CLIENT to the compiled client (tests/ts_build.py)");
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
const { Indox } = createRequire(import.meta.url)(clientPath);
const client = new Indox({ apiKey: key, baseUrl: base, timeoutMs: 60_000 });

// Exact generated operation ids: if codegen renames one, this must break loudly.
const PROBES = [
  ["health", () => client.health.commonHealthViewsHealth()],
  ["fonts.formats", () => client.fonts.appsFontsViewsFormatsListFormats()],
  ["pdf.formats", () => client.pdf.appsPdfHandlerViewsFormatsViewsGetSupportedDocumentTypes()],
  ["image.formats", () => client.images.convertImageFormatsRetrieve()],
];
// 401/403 is soft above, so an invalid key would score a clean board. This one
// is 2xx only for an authenticated caller.
const SENTINEL = ["webhooks.list", () => client.webhooks.appsWebhooksViewsCrudListWebhooks()];

async function statusOf(call) {
  try {
    await call();
    return 200;
  } catch (err) {
    const status = err?.response?.status;
    if (typeof status === "number") return status;
    throw err;
  }
}

async function probe(label, call) {
  const status = await statusOf(call);
  if (status >= 500) throw new Error(`${label}: HTTP ${status}`);
  if (status >= 400 && !soft.has(status)) throw new Error(`${label}: unexpected HTTP ${status}`);
  console.log(`  PASS ${label} (HTTP ${status})`);
}

async function main() {
  console.log(`@indox/sdk smoke via src/client.ts base=${base}`);
  for (const [label, call] of PROBES) await probe(label, call);
  const [label, call] = SENTINEL;
  const status = await statusOf(call);
  if (status < 200 || status >= 300) {
    throw new Error(
      `auth sentinel ${label}: HTTP ${status}, expected 2xx` +
        " — the API key is missing, wrong, expired or revoked",
    );
  }
  console.log(`  PASS ${label} (HTTP ${status}, auth sentinel)`);
  console.log("OK typescript smoke");
}

main().catch((err) => {
  console.error("FAIL", err.message || err);
  process.exit(1);
});
