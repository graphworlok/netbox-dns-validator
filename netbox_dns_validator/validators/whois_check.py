"""
WHOIS check: queries live WHOIS data for a zone name.

Internet is the source of truth — we report what registrar/expiry/EPP
statuses the domain actually has, so operators can spot discrepancies
with what they expect in netbox-dns.
"""

import datetime
import logging

import whois

logger = logging.getLogger(__name__)

# EPP statuses that indicate a problem worth flagging
_PROBLEM_STATUSES = {
    "pendingDelete",
    "redemptionPeriod",
    "pendingRestore",
    "serverHold",
    "clientHold",
}


def check(zone_name: str, timeout: int = 10) -> dict:
    """
    Returns a dict:
      {
        "ok": bool,
        "registrar": str,
        "expiry": date | None,
        "epp_statuses": [str, ...],
        "warning": bool,   # True if concerning EPP status seen
        "error": str,      # non-empty on lookup failure
      }
    """
    result = {
        "ok": False,
        "registrar": "",
        "expiry": None,
        "epp_statuses": [],
        "warning": False,
        "error": "",
    }

    try:
        w = whois.whois(zone_name)
    except Exception as exc:
        result["error"] = str(exc)
        logger.warning("WHOIS lookup failed for %s: %s", zone_name, exc)
        return result

    # Registrar
    result["registrar"] = w.registrar or ""

    # Expiry — may be a list
    expiry = w.expiration_date
    if isinstance(expiry, list):
        expiry = expiry[0]
    if isinstance(expiry, datetime.datetime):
        expiry = expiry.date()
    result["expiry"] = expiry

    # EPP statuses — normalise to a sorted list of bare status strings
    raw_statuses = w.status or []
    if isinstance(raw_statuses, str):
        raw_statuses = [raw_statuses]
    # Strip any trailing URL that registrars append
    clean = sorted({s.split()[0] for s in raw_statuses if s})
    result["epp_statuses"] = clean

    result["warning"] = bool(_PROBLEM_STATUSES & set(clean))
    result["ok"] = True
    return result
