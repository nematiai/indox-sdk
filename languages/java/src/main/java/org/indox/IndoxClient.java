package org.indox;

/**
 * Thin Indox client — resolves Bearer API key and base URL for the generated SDK.
 */
public final class IndoxClient {
  private final String apiKey;
  private final String baseUrl;

  public IndoxClient(String apiKey, String baseUrl) {
    if (apiKey == null || apiKey.isBlank()) {
      throw new IllegalArgumentException("apiKey required (or set INDOX_API_KEY)");
    }
    this.apiKey = apiKey.trim();
    this.baseUrl = (baseUrl == null || baseUrl.isBlank())
        ? "https://indox.org"
        : baseUrl.replaceAll("/+$", "");
  }

  public static IndoxClient fromEnv() {
    String key = System.getenv().getOrDefault("INDOX_API_KEY", "");
    String base = System.getenv().getOrDefault("INDOX_BASE_URL", "https://indox.org");
    return new IndoxClient(key, base);
  }

  public String getApiKey() {
    return apiKey;
  }

  public String getBaseUrl() {
    return baseUrl;
  }

  public String authorizationHeader() {
    return "Bearer " + apiKey;
  }
}
