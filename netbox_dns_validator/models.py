from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .choices import ValidationStatusChoices


class ZoneValidation(NetBoxModel):
    """
    Stores the most recent zone-level validation result for a netbox-dns Zone.

    Covers three checks:
      - WHOIS: registrar, expiry date, EPP status codes
      - NS delegation: nameservers at the registrar/parent match netbox-dns config
      - Resolver: each configured nameserver is authoritative and responding
    """

    zone = models.OneToOneField(
        "netbox_dns.Zone",
        on_delete=models.CASCADE,
        related_name="validation",
    )

    checked_at = models.DateTimeField(null=True, blank=True, verbose_name="Last Checked")

    overall_status = models.CharField(
        max_length=16,
        choices=ValidationStatusChoices,
        default=ValidationStatusChoices.UNKNOWN,
        verbose_name="Status",
    )

    # --- WHOIS ---
    whois_status = models.CharField(
        max_length=16,
        choices=ValidationStatusChoices,
        default=ValidationStatusChoices.UNKNOWN,
    )
    whois_registrar = models.CharField(max_length=256, blank=True)
    whois_expiry = models.DateField(null=True, blank=True, verbose_name="WHOIS Expiry")
    whois_epp_statuses = models.JSONField(
        default=list,
        blank=True,
        verbose_name="EPP Status Codes",
        help_text="Domain EPP/RDAP status codes from WHOIS (e.g. clientTransferProhibited)",
    )
    whois_server_used = models.CharField(
        max_length=256,
        blank=True,
        verbose_name="WHOIS Server",
        help_text="WHOIS server queried (blank = python-whois default for this TLD)",
    )
    whois_error = models.TextField(blank=True)

    # --- NS Delegation ---
    ns_status = models.CharField(
        max_length=16,
        choices=ValidationStatusChoices,
        default=ValidationStatusChoices.UNKNOWN,
        verbose_name="NS Delegation Status",
    )
    ns_configured = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Configured Nameservers",
        help_text="Nameservers as configured in netbox-dns",
    )
    ns_delegated = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Delegated Nameservers",
        help_text="Nameservers seen in parent zone / public resolvers",
    )
    ns_missing = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Missing from Delegation",
        help_text="In netbox-dns but not delegated",
    )
    ns_extra = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Extra in Delegation",
        help_text="Delegated but not in netbox-dns",
    )
    ns_error = models.TextField(blank=True)

    # --- Resolver / Authoritative check ---
    resolver_status = models.CharField(
        max_length=16,
        choices=ValidationStatusChoices,
        default=ValidationStatusChoices.UNKNOWN,
        verbose_name="Resolver Status",
    )
    resolver_results = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Per-Nameserver Results",
        help_text="Keyed by nameserver hostname: {ok, ip, serial, error}",
    )
    resolver_error = models.TextField(blank=True)

    class Meta:
        ordering = ["zone__name"]
        verbose_name = "Zone Validation"
        verbose_name_plural = "Zone Validations"

    def __str__(self):
        return f"Validation: {self.zone.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns_validator:zonevalidation", args=[self.pk])

    def _worst_status(self, *statuses):
        rank = {
            ValidationStatusChoices.UNKNOWN: 0,
            ValidationStatusChoices.PASS: 1,
            ValidationStatusChoices.WARNING: 2,
            ValidationStatusChoices.FAIL: 3,
        }
        return max(statuses, key=lambda s: rank.get(s, 0))

    def recompute_overall(self):
        self.overall_status = self._worst_status(
            self.whois_status,
            self.ns_status,
            self.resolver_status,
        )
