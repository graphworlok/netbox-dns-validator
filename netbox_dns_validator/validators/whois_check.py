"""
WHOIS check: queries live WHOIS data for a zone name.

Internet is the source of truth — we report what registrar/expiry/EPP
statuses the domain actually has.

TLD handling
------------
python-whois ships its own WHOIS server map, but coverage is uneven:
  - Some ccTLDs (e.g. .de, .au) use non-standard formats or rate-limit heavily
  - Some TLDs publish no WHOIS at all (private/internal, some new gTLDs)
  - A handful of registries have migrated to RDAP-only

To cope, the plugin exposes two settings in PLUGINS_CONFIG:

  whois_servers  : dict mapping TLD suffix → WHOIS server hostname override
                   (e.g. {"au": "whois.auda.org.au", "co.uk": "whois.nic.uk"})

  whois_skip_tlds: list of TLD suffixes to skip instead of querying
                   (returns status "unknown" with a note rather than "fail")

Empty results (no registrar, no error) are treated as WARNING rather than PASS
because many ccTLD registries suppress registrar data but the domain is live.
"""

import datetime
import logging

import whois

logger = logging.getLogger(__name__)

_PROBLEM_STATUSES = {
    "pendingDelete",
    "redemptionPeriod",
    "pendingRestore",
    "serverHold",
    "clientHold",
}


def _extract_tld(zone_name: str) -> str:
    """
    Return the effective TLD suffix for lookup purposes.

    Checks multi-label suffixes (up to 3 labels) before falling back to the
    single last label.  The caller's whois_servers map wins if it contains a
    matching key, so we return the longest matching suffix we can find.

    e.g. "example.co.uk" → "co.uk"  (if "co.uk" is in whois_servers)
         "example.com.au" → "com.au" (if "com.au" is in whois_servers)
         "example.com"    → "com"
    """
    labels = zone_name.rstrip(".").lower().split(".")
    # Return the raw labels so the caller can do longest-match
    return labels


def _match_tld(labels: list[str], server_map: dict) -> tuple[str, str | None]:
    """
    Return (matched_suffix, server_or_None) using longest-match against
    server_map keys.  server_map keys should NOT have a leading dot.
    """
    for n in range(min(3, len(labels) - 1), 0, -1):
        suffix = ".".join(labels[-n:])
        if suffix in server_map:
            return suffix, server_map[suffix]
    # No override found; return the single-label TLD with no server
    return labels[-1], None


def check(
    zone_name: str,
    whois_servers: dict | None = None,
    whois_skip_tlds: list | None = None,
    timeout: int = 10,
) -> dict:
    """
    Returns a dict:
      {
        "ok": bool,
        "skipped": bool,       # True when the TLD is in whois_skip_tlds
        "registrar": str,
        "expiry": date | None,
        "epp_statuses": [str, ...],
        "warning": bool,       # True if concerning EPP status OR empty result
        "tld": str,            # matched TLD suffix
        "server": str | None,  # WHOIS server used (if override applied)
        "error": str,
      }
    """
    whois_servers = whois_servers or {}
    whois_skip_tlds = whois_skip_tlds or []

    result = {
        "ok": False,
        "skipped": False,
        "registrar": "",
        "expiry": None,
        "epp_statuses": [],
        "warning": False,
        "tld": "",
        "server": None,
        "error": "",
    }

    labels = _extract_tld(zone_name)
    matched_suffix, override_server = _match_tld(labels, whois_servers)
    result["tld"] = matched_suffix
    result["server"] = override_server

    # Check skip list (longest-match too)
    skip_set = {s.lstrip(".").lower() for s in whois_skip_tlds}
    for n in range(min(3, len(labels) - 1), 0, -1):
        suffix = ".".join(labels[-n:])
        if suffix in skip_set:
            result["skipped"] = True
            result["ok"] = True  # not a failure — intentionally skipped
            result["error"] = f"WHOIS skipped for .{suffix} (in whois_skip_tlds)"
            return result

    # Query WHOIS
    try:
        kwargs = {}
        if override_server:
            kwargs["server"] = override_server
        w = whois.whois(zone_name, **kwargs)
    except Exception as exc:
        result["error"] = str(exc)
        logger.warning("WHOIS lookup failed for %s: %s", zone_name, exc)
        return result

    # Registrar
    result["registrar"] = w.registrar or ""

    # Expiry
    expiry = w.expiration_date
    if isinstance(expiry, list):
        expiry = expiry[0]
    if isinstance(expiry, datetime.datetime):
        expiry = expiry.date()
    result["expiry"] = expiry

    # EPP statuses
    raw_statuses = w.status or []
    if isinstance(raw_statuses, str):
        raw_statuses = [raw_statuses]
    clean = sorted({s.split()[0] for s in raw_statuses if s})
    result["epp_statuses"] = clean

    # Treat empty registrar as a warning — many ccTLDs withhold it
    empty_result = not result["registrar"] and not result["expiry"] and not clean
    result["warning"] = empty_result or bool(_PROBLEM_STATUSES & set(clean))

    if empty_result:
        result["error"] = (
            f"WHOIS returned no data for .{matched_suffix} — "
            "registry may restrict WHOIS output; consider adding a whois_servers override"
        )

    result["ok"] = True
    return result
