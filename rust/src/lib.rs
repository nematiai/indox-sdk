//! Thin Indox client — Bearer API key + health probe.

use std::time::Duration;

use reqwest::Client;
use thiserror::Error;

const CONNECT_TIMEOUT: Duration = Duration::from_secs(5);
const REQUEST_TIMEOUT: Duration = Duration::from_secs(60);

#[derive(Debug, Error)]
pub enum IndoxError {
    #[error("missing INDOX_API_KEY")]
    MissingKey,
    #[error(transparent)]
    Http(#[from] reqwest::Error),
    #[error("HTTP {status}: response body was not valid JSON")]
    Decode {
        status: u16,
        #[source]
        source: serde_json::Error,
    },
}

pub struct Indox {
    api_key: String,
    base_url: String,
    http: Client,
}

impl Indox {
    pub fn from_env() -> Result<Self, IndoxError> {
        let api_key = std::env::var("INDOX_API_KEY").map_err(|_| IndoxError::MissingKey)?;
        let base_url = std::env::var("INDOX_BASE_URL").unwrap_or_else(|_| "https://indox.org".into());
        Ok(Self {
            api_key: api_key.trim().to_string(),
            base_url: base_url.trim_end_matches('/').to_string(),
            http: Client::builder()
                .connect_timeout(CONNECT_TIMEOUT)
                .timeout(REQUEST_TIMEOUT)
                .build()?,
        })
    }

    pub async fn get_json(&self, path: &str) -> Result<(u16, serde_json::Value), IndoxError> {
        let url = format!("{}{}", self.base_url, path);
        let res = self
            .http
            .get(url)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header("Accept", "application/json")
            .send()
            .await?;
        let status = res.status().as_u16();
        let bytes = res.bytes().await?;
        if bytes.is_empty() {
            return Ok((status, serde_json::Value::Null));
        }
        let body = serde_json::from_slice(&bytes)
            .map_err(|source| IndoxError::Decode { status, source })?;
        Ok((status, body))
    }

    pub async fn health(&self) -> Result<(u16, serde_json::Value), IndoxError> {
        self.get_json("/api/v1/health/").await
    }
}
