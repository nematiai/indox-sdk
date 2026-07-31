# frozen_string_literal: true

require "net/http"
require "json"
require "uri"

# Thin Indox client — Bearer API key + health probe helper.
module IndoxClient
  class Error < StandardError; end

  OPEN_TIMEOUT = 5
  READ_TIMEOUT = 60

  class Client
    attr_reader :api_key, :base_url

    def initialize(api_key: ENV.fetch("INDOX_API_KEY", ""), base_url: ENV.fetch("INDOX_BASE_URL", "https://indox.org"))
      raise Error, "api_key required" if api_key.to_s.strip.empty?
      @api_key = api_key.strip
      @base_url = base_url.to_s.sub(%r{/*$}, "")
    end

    def get(path)
      uri = URI.join("#{@base_url}/", path.sub(%r{^/}, ""))
      req = Net::HTTP::Get.new(uri)
      req["Authorization"] = "Bearer #{api_key}"
      req["Accept"] = "application/json"
      Net::HTTP.start(
        uri.host,
        uri.port,
        use_ssl: uri.scheme == "https",
        open_timeout: OPEN_TIMEOUT,
        read_timeout: READ_TIMEOUT,
        write_timeout: READ_TIMEOUT
      ) do |http|
        http.request(req)
      end
    end

    def health
      get("/api/v1/health/")
    end
  end
end
