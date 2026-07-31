package indox

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

// Client is a thin HTTP helper around the Indox API v1 allowlist.
type Client struct {
	APIKey  string
	BaseURL string
	HTTP    *http.Client
}

// NewFromEnv builds a client from INDOX_API_KEY / INDOX_BASE_URL.
func NewFromEnv() (*Client, error) {
	key := strings.TrimSpace(os.Getenv("INDOX_API_KEY"))
	if key == "" {
		return nil, fmt.Errorf("INDOX_API_KEY required")
	}
	base := strings.TrimRight(os.Getenv("INDOX_BASE_URL"), "/")
	if base == "" {
		base = "https://indox.org"
	}
	return &Client{
		APIKey:  key,
		BaseURL: base,
		HTTP:    &http.Client{Timeout: 60 * time.Second},
	}, nil
}

// Get issues an authenticated GET and returns status + body.
func (c *Client) Get(path string) (int, []byte, error) {
	if !strings.HasPrefix(path, "/") {
		path = "/" + path
	}
	req, err := http.NewRequest(http.MethodGet, c.BaseURL+path, nil)
	if err != nil {
		return 0, nil, err
	}
	req.Header.Set("Authorization", "Bearer "+c.APIKey)
	req.Header.Set("Accept", "application/json")
	res, err := c.HTTP.Do(req)
	if err != nil {
		return 0, nil, err
	}
	defer res.Body.Close()
	body, err := io.ReadAll(res.Body)
	return res.StatusCode, body, err
}

// Health calls GET /api/v1/health/.
func (c *Client) Health() (int, []byte, error) {
	return c.Get("/api/v1/health/")
}
