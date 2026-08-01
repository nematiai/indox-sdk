/**
 * Thin Indox client over the generated OpenAPI fetch SDK.
 * Auth: Bearer API key via INDOX_API_KEY or constructor.
 */
import {
  Configuration,
  HealthApi,
  FontConversionApi,
  PDFHandlerApi,
  CoreApi,
  ImageConverterApi,
  VideoConverterApi,
  ModelConverterApi,
  WebhooksApi,
} from "../generated/src/index.js";

export type IndoxOptions = {
  apiKey?: string;
  baseUrl?: string;
  timeoutMs?: number;
};

const DEFAULT_TIMEOUT_MS = 60_000;

function resolveKey(explicit?: string): string {
  const key = (explicit || process.env.INDOX_API_KEY || "").trim();
  if (!key) {
    throw new Error("Set apiKey or INDOX_API_KEY");
  }
  return key;
}

type SignalStatics = {
  timeout(ms: number): AbortSignal;
  any?(signals: AbortSignal[]): AbortSignal;
};

function timeoutFetch(timeoutMs: number) {
  return (input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> => {
    const statics = AbortSignal as unknown as SignalStatics;
    const deadline = statics.timeout(timeoutMs);
    const signal =
      init.signal && statics.any ? statics.any([init.signal, deadline]) : init.signal || deadline;
    return fetch(input, { ...init, signal });
  };
}

export class Indox {
  readonly config: Configuration;
  readonly health: HealthApi;
  readonly fonts: FontConversionApi;
  readonly pdf: PDFHandlerApi;
  readonly docs: CoreApi;
  // docs_core and media_core share one generated tag, so both read from CoreApi.
  readonly media: CoreApi;
  readonly images: ImageConverterApi;
  readonly videos: VideoConverterApi;
  readonly models: ModelConverterApi;
  readonly webhooks: WebhooksApi;

  constructor(opts: IndoxOptions = {}) {
    const apiKey = resolveKey(opts.apiKey);
    const basePath = (opts.baseUrl || process.env.INDOX_BASE_URL || "https://indox.org").replace(
      /\/+$/,
      "",
    );
    this.config = new Configuration({
      basePath,
      accessToken: apiKey,
      headers: { Authorization: `Bearer ${apiKey}` },
      fetchApi: timeoutFetch(opts.timeoutMs ?? DEFAULT_TIMEOUT_MS),
    });
    this.health = new HealthApi(this.config);
    this.fonts = new FontConversionApi(this.config);
    this.pdf = new PDFHandlerApi(this.config);
    this.docs = new CoreApi(this.config);
    this.media = this.docs;
    this.images = new ImageConverterApi(this.config);
    this.videos = new VideoConverterApi(this.config);
    this.models = new ModelConverterApi(this.config);
    this.webhooks = new WebhooksApi(this.config);
  }

  /** Poll until conversion reaches a terminal-ish status or timeout. */
  async waitJson(
    getter: () => Promise<Record<string, unknown>>,
    opts: { intervalMs?: number; timeoutMs?: number } = {},
  ): Promise<Record<string, unknown>> {
    const intervalMs = opts.intervalMs ?? 2000;
    const timeoutMs = opts.timeoutMs ?? 300_000;
    const start = Date.now();
    const done = new Set(["completed", "done", "success", "failed", "error", "cancelled"]);
    for (;;) {
      const body = await getter();
      const status = String(body.status || body.state || "").toLowerCase();
      if (done.has(status)) return body;
      if (Date.now() - start > timeoutMs) {
        throw new Error(`wait timed out after ${timeoutMs}ms (last status=${status || "?"})`);
      }
      await new Promise((r) => setTimeout(r, intervalMs));
    }
  }
}

export * from "../generated/src/index.js";
