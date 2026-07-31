using System;
using System.Net.Http;
using System.Net.Http.Headers;

namespace Indox.Sdk;

/// <summary>Thin helper: Bearer API key + base URL for the generated client.</summary>
public sealed class IndoxClient
{
    public string ApiKey { get; }
    public string BaseUrl { get; }

    public IndoxClient(string? apiKey = null, string? baseUrl = null)
    {
        ApiKey = (apiKey ?? Environment.GetEnvironmentVariable("INDOX_API_KEY") ?? "").Trim();
        if (string.IsNullOrEmpty(ApiKey))
            throw new ArgumentException("apiKey required (or set INDOX_API_KEY)");
        BaseUrl = (baseUrl ?? Environment.GetEnvironmentVariable("INDOX_BASE_URL") ?? "https://indox.org")
            .TrimEnd('/');
    }

    public HttpClient CreateHttpClient()
    {
        var http = new HttpClient { BaseAddress = new Uri(BaseUrl + "/") };
        http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", ApiKey);
        http.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        return http;
    }
}
