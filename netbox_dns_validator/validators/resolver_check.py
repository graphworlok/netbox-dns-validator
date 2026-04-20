"""
Resolver / authoritative check: queries each configured nameserver
directly for the zone's SOA record and verifies it answers authoritatively.

Internet is the source of truth — we report the actual SOA serial and
whether each nameserver is responding, so operators can spot stale or
broken nameservers.
"""

import logging
import socket

import dns.exception
import dns.flags
import dns.message
import dns.name
import dns.query
import dns.rdatatype

logger = logging.getLogger(__name__)


def _resolve_ns_ip(nameserver: str, timeout: int) -> str | None:
    try:
        return socket.getaddrinfo(nameserver, None, socket.AF_INET)[0][4][0]
    except OSError:
        try:
            return socket.getaddrinfo(nameserver, None, socket.AF_INET6)[0][4][0]
        except OSError:
            return None


def _query_soa(zone_name: str, ns_ip: str, timeout: int) -> dict:
    qname = dns.name.from_text(zone_name)
    request = dns.message.make_query(qname, dns.rdatatype.SOA)
    try:
        response = dns.query.udp(request, ns_ip, timeout=timeout)
    except dns.exception.Timeout:
        return {"ok": False, "authoritative": False, "serial": None, "error": "Timeout"}
    except Exception as exc:
        return {"ok": False, "authoritative": False, "serial": None, "error": str(exc)}

    authoritative = bool(response.flags & dns.flags.AA)
    serial = None

    for rrset in response.answer:
        if rrset.rdtype == dns.rdatatype.SOA:
            serial = rrset[0].serial
            break

    if not authoritative:
        return {"ok": False, "authoritative": False, "serial": serial, "error": "Not authoritative"}

    return {"ok": True, "authoritative": True, "serial": serial, "error": ""}


def check(zone_name: str, nameservers: list[str], timeout: int = 10) -> dict:
    """
    Returns a dict:
      {
        "ok": bool,              # True if ALL nameservers responded authoritatively
        "results": {
          "<ns_hostname>": {
            "ok": bool,
            "ip": str | None,
            "authoritative": bool,
            "serial": int | None,
            "error": str,
          },
          ...
        },
        "error": str,
      }
    """
    results = {}

    if not nameservers:
        return {"ok": False, "results": {}, "error": "No nameservers configured in netbox-dns"}

    for ns in nameservers:
        ns_ip = _resolve_ns_ip(ns, timeout)
        if not ns_ip:
            results[ns] = {
                "ok": False,
                "ip": None,
                "authoritative": False,
                "serial": None,
                "error": f"Could not resolve {ns} to an IP address",
            }
            continue

        soa = _query_soa(zone_name, ns_ip, timeout)
        results[ns] = {"ip": ns_ip, **soa}

    all_ok = all(v["ok"] for v in results.values())
    return {"ok": all_ok, "results": results, "error": ""}
