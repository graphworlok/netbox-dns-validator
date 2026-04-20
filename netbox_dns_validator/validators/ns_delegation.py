"""
NS delegation check: queries public resolvers for the NS records the
parent zone is delegating for this zone.

Internet is the source of truth. We compare those NS records against
the nameservers configured in netbox-dns and report any gaps.
"""

import logging

import dns.exception
import dns.name
import dns.resolver

logger = logging.getLogger(__name__)


def _query_ns(zone_name: str, resolvers: list[str], timeout: int) -> list[str]:
    """Return sorted list of delegated NS hostnames from a public resolver."""
    r = dns.resolver.Resolver()
    r.nameservers = resolvers
    r.timeout = timeout
    r.lifetime = timeout

    answer = r.resolve(zone_name, "NS")
    return sorted(str(rdata.target).rstrip(".").lower() for rdata in answer)


def check(zone_name: str, configured_ns: list[str], resolvers: list[str], timeout: int = 10) -> dict:
    """
    Returns a dict:
      {
        "ok": bool,
        "delegated": [str, ...],   # NS seen on the internet
        "configured": [str, ...],  # NS from netbox-dns (normalised)
        "missing": [str, ...],     # in netbox-dns but NOT delegated
        "extra": [str, ...],       # delegated but NOT in netbox-dns
        "match": bool,
        "error": str,
      }
    """
    norm_configured = sorted(n.rstrip(".").lower() for n in configured_ns)

    result = {
        "ok": False,
        "delegated": [],
        "configured": norm_configured,
        "missing": [],
        "extra": [],
        "match": False,
        "error": "",
    }

    try:
        delegated = _query_ns(zone_name, resolvers, timeout)
    except dns.resolver.NXDOMAIN:
        result["error"] = "Zone not found in DNS (NXDOMAIN)"
        return result
    except dns.resolver.NoAnswer:
        result["error"] = "No NS records returned by resolver"
        return result
    except dns.exception.DNSException as exc:
        result["error"] = str(exc)
        logger.warning("NS delegation query failed for %s: %s", zone_name, exc)
        return result

    configured_set = set(norm_configured)
    delegated_set = set(delegated)

    result["ok"] = True
    result["delegated"] = delegated
    result["missing"] = sorted(configured_set - delegated_set)
    result["extra"] = sorted(delegated_set - configured_set)
    result["match"] = not result["missing"] and not result["extra"]
    return result
