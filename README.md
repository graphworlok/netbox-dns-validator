# netbox-dns-validator

A [NetBox](https://github.com/netbox-community/netbox) plugin that audits DNS zones against live internet data.

It uses a [netbox-dns](https://github.com/peteeckel/netbox-plugin-dns) view as the list of zones to check, then queries the internet as the source of truth — surfacing discrepancies in registrar data, NS delegation, and authoritative resolver responses.

## Checks performed

| Check | What it validates |
|---|---|
| **WHOIS** | Registrar, expiry date, EPP status codes (flags problem statuses like `pendingDelete`, `serverHold`) |
| **NS Delegation** | Nameservers delegated at the parent zone / registrar vs nameservers configured in netbox-dns |
| **Resolvers** | Each configured nameserver is reachable, answers authoritatively, and returns a SOA serial |

Results are stored per zone and displayed in the NetBox UI with pass/warning/fail badges.

## Requirements

- NetBox >= 4.0.0
- [netbox-dns](https://github.com/peteeckel/netbox-plugin-dns) (Peter Eckel's plugin)
- Python >= 3.10
- `dnspython >= 2.4`
- `python-whois >= 0.9`

## Installation

### 1. Install the package

From PyPI (once published):
```bash
pip install netbox-dns-validator
```

From this repository:
```bash
pip install git+https://github.com/graphworlok/netbox-dns-validator.git
```

Or clone and install editable for development:
```bash
git clone https://github.com/graphworlok/netbox-dns-validator.git
pip install -e ./netbox-dns-validator
```

### 2. Add to NetBox configuration

In `configuration.py`:

```python
PLUGINS = [
    "netbox_dns",           # must already be present
    "netbox_dns_validator",
]

PLUGINS_CONFIG = {
    "netbox_dns_validator": {
        # Public resolvers used for NS delegation checks
        "public_resolvers": ["8.8.8.8", "1.1.1.1"],
        # Seconds before a DNS or WHOIS query times out
        "query_timeout": 10,
        # Optional: static per-TLD WHOIS server overrides (see TLD Config below)
        "whois_servers": {},
        # Optional: TLD suffixes to skip WHOIS for entirely
        "whois_skip_tlds": [],
    }
}
```

### 3. Run migrations and restart

```bash
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

The plugin appears in the NetBox navigation under **DNS Validator**.

## Usage

1. Navigate to **DNS Validator → Validate a View**
2. Select a netbox-dns view
3. Click **Run Validation** — all zones in the view are checked and results stored
4. View per-zone results under **DNS Validator → Zone Results**
5. Click any zone to see the full WHOIS / NS delegation / resolver breakdown
6. Use the **Re-validate** button on a zone detail page to re-run checks for a single zone

## TLD WHOIS configuration

WHOIS quality varies significantly across TLDs. Some ccTLDs use non-standard
servers, rate-limit aggressively, or suppress registrar data entirely.

You can manage per-TLD overrides via **DNS Validator → Configuration → TLD WHOIS Config** without editing `configuration.py`:

| Field | Purpose |
|---|---|
| **TLD Suffix** | Suffix without leading dot — multi-part supported, e.g. `co.uk`, `com.au` |
| **WHOIS Server** | Override server hostname; leave blank to use python-whois default |
| **Skip WHOIS** | Suppress WHOIS for this TLD entirely — result shows as Unknown rather than Fail |
| **Notes** | Free text to document why an override exists |

GUI records take precedence over `PLUGINS_CONFIG` at validation time. Common examples:

| TLD | Server |
|---|---|
| `au` | `whois.auda.org.au` |
| `co.uk` | `whois.nic.uk` |
| `de` | `whois.denic.de` |
| `nz` | `whois.nic.nz` |

TLDs that return empty results (no registrar, no expiry, no EPP statuses) are flagged as **Warning** rather than Pass, with a prompt to add a server override.

Private or internal TLDs (e.g. `local`, `internal`, `corp`) should be added to the skip list so they show **Unknown** rather than polluting the failure count.

## Status meanings

| Status | Meaning |
|---|---|
| **Pass** | Check completed and data looks correct |
| **Warning** | Check completed but something warrants attention (e.g. NS mismatch, empty WHOIS, problem EPP status) |
| **Fail** | Check failed — query error, NXDOMAIN, nameserver not authoritative |
| **Unknown** | Check not yet run, or intentionally skipped (skip-TLD) |

The **Overall** status for a zone is the worst of its three individual check statuses.

## License

MIT
