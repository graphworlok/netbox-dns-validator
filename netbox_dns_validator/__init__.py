from netbox.plugins import PluginConfig


class DNSValidatorConfig(PluginConfig):
    name = "netbox_dns_validator"
    verbose_name = "DNS Zone Validator"
    description = "Validates NetBox DNS zones against live WHOIS, NS delegation, and resolver data"
    version = "0.1.0"
    author = "graphworlok"
    base_url = "dns-validator"
    min_version = "4.0.0"
    required_settings = []

    default_settings = {
        # Public resolvers used for NS delegation checks
        "public_resolvers": ["8.8.8.8", "1.1.1.1"],
        # Seconds before a DNS/WHOIS query times out
        "query_timeout": 10,
        # Proxy for outbound requests (e.g. "http://proxy:3128")
        "http_proxy": None,
        # Per-TLD WHOIS server overrides. Key is the TLD suffix (without leading
        # dot); value is the WHOIS server hostname to query directly.
        # Multi-part suffixes are supported (e.g. "co.uk": "whois.nic.uk").
        # Example:
        #   "whois_servers": {
        #       "au":    "whois.auda.org.au",
        #       "co.uk": "whois.nic.uk",
        #       "de":    "whois.denic.de",
        #   }
        "whois_servers": {},
        # TLD suffixes (without leading dot) for which WHOIS should be skipped
        # entirely rather than attempted. Zones matching these will show status
        # "unknown" with a note, rather than "fail".
        # Useful for private/internal TLDs or ccTLDs with restricted WHOIS.
        # Example: ["local", "internal", "arpa"]
        "whois_skip_tlds": [],
    }

    def ready(self):
        pass


config = DNSValidatorConfig
