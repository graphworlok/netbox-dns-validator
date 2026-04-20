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
    }

    def ready(self):
        pass


config = DNSValidatorConfig
