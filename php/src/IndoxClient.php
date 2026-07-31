<?php
declare(strict_types=1);

namespace Indox;

/**
 * Thin wrapper: Bearer API key + base URL for generated Indox OpenAPI client.
 */
final class IndoxClient
{
    public function __construct(
        public readonly string $apiKey,
        public readonly string $baseUrl = 'https://indox.org',
    ) {
        if ($apiKey === '') {
            throw new \InvalidArgumentException('apiKey required (or set INDOX_API_KEY)');
        }
    }

    public static function fromEnv(): self
    {
        $key = trim((string) (getenv('INDOX_API_KEY') ?: ''));
        $base = rtrim((string) (getenv('INDOX_BASE_URL') ?: 'https://indox.org'), '/');
        return new self($key, $base);
    }

    /** @return array{Authorization: string, Accept: string} */
    public function authHeaders(): array
    {
        return [
            'Authorization' => 'Bearer ' . $this->apiKey,
            'Accept' => 'application/json',
        ];
    }
}
