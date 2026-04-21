"""
Orchestrates all zone-level checks and persists results to ZoneValidation.
"""

import logging
from datetime import timezone

from django.utils import timezone as dj_timezone
from django.conf import settings

from ..choices import ValidationStatusChoices
from . import whois_check, ns_delegation, resolver_check

logger = logging.getLogger(__name__)


def _plugin_setting(key):
    cfg = settings.PLUGINS_CONFIG.get("netbox_dns_validator", {})
    defaults = {
        "public_resolvers": ["8.8.8.8", "1.1.1.1"],
        "query_timeout": 10,
        "whois_servers": {},
        "whois_skip_tlds": [],
    }
    return cfg.get(key, defaults[key])


def _status_from_check(ok: bool, warning: bool = False) -> str:
    if not ok:
        return ValidationStatusChoices.FAIL
    if warning:
        return ValidationStatusChoices.WARNING
    return ValidationStatusChoices.PASS


def _merged_whois_config() -> tuple[dict, list]:
    """
    Return (whois_servers, whois_skip_tlds) merged from PLUGINS_CONFIG and DB.
    DB records take precedence over static config.
    """
    from ..models import TLDWhoisConfig

    servers = dict(_plugin_setting("whois_servers"))
    skip = set(_plugin_setting("whois_skip_tlds"))

    for cfg in TLDWhoisConfig.objects.all():
        tld = cfg.tld.lstrip(".").lower()
        if cfg.skip:
            skip.add(tld)
            servers.pop(tld, None)
        else:
            skip.discard(tld)
            if cfg.whois_server:
                servers[tld] = cfg.whois_server
            else:
                servers.pop(tld, None)

    return servers, sorted(skip)


def validate_zone(zone) -> "ZoneValidation":
    """
    Run all checks for a single netbox-dns Zone instance.
    Creates or updates the ZoneValidation record and returns it.
    """
    from ..models import ZoneValidation

    resolvers = _plugin_setting("public_resolvers")
    timeout = _plugin_setting("query_timeout")
    whois_servers, whois_skip_tlds = _merged_whois_config()

    zone_name = zone.name.rstrip(".")
    configured_ns = [ns.name.rstrip(".").lower() for ns in zone.nameservers.all()]

    validation, _ = ZoneValidation.objects.get_or_create(zone=zone)

    # --- WHOIS ---
    logger.info("WHOIS check: %s", zone_name)
    w = whois_check.check(
        zone_name,
        whois_servers=whois_servers,
        whois_skip_tlds=whois_skip_tlds,
        timeout=timeout,
    )
    validation.whois_registrar = w["registrar"]
    validation.whois_expiry = w["expiry"]
    validation.whois_epp_statuses = w["epp_statuses"]
    validation.whois_server_used = w.get("server") or ""
    validation.whois_error = w["error"]
    if w["skipped"]:
        validation.whois_status = ValidationStatusChoices.UNKNOWN
    elif not w["ok"]:
        validation.whois_status = ValidationStatusChoices.FAIL
    elif w["warning"]:
        validation.whois_status = ValidationStatusChoices.WARNING
    else:
        validation.whois_status = ValidationStatusChoices.PASS

    # --- NS Delegation ---
    logger.info("NS delegation check: %s", zone_name)
    ns = ns_delegation.check(zone_name, configured_ns, resolvers=resolvers, timeout=timeout)
    validation.ns_configured = ns["configured"]
    validation.ns_delegated = ns["delegated"]
    validation.ns_missing = ns["missing"]
    validation.ns_extra = ns["extra"]
    validation.ns_error = ns["error"]
    if not ns["ok"]:
        validation.ns_status = ValidationStatusChoices.FAIL
    elif not ns["match"]:
        validation.ns_status = ValidationStatusChoices.WARNING
    else:
        validation.ns_status = ValidationStatusChoices.PASS

    # --- Resolver ---
    logger.info("Resolver check: %s", zone_name)
    res = resolver_check.check(zone_name, configured_ns, timeout=timeout)
    validation.resolver_results = res["results"]
    validation.resolver_error = res["error"]
    validation.resolver_status = _status_from_check(res["ok"])

    # --- Overall ---
    validation.checked_at = dj_timezone.now()
    validation.recompute_overall()
    validation.save()

    return validation
