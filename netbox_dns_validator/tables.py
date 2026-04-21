import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from .models import TLDWhoisConfig, ZoneValidation
from .choices import ValidationStatusChoices

_BADGE_MAP = {
    ValidationStatusChoices.PASS: "success",
    ValidationStatusChoices.WARNING: "warning",
    ValidationStatusChoices.FAIL: "danger",
    ValidationStatusChoices.UNKNOWN: "secondary",
}


class StatusBadgeColumn(tables.Column):
    def render(self, value):
        label = value.capitalize()
        css = _BADGE_MAP.get(value, "secondary")
        return tables.utils.mark_safe(
            f'<span class="badge bg-{css}">{label}</span>'
        )


class TLDWhoisConfigTable(NetBoxTable):
    tld = tables.Column(linkify=True, verbose_name="TLD Suffix")
    whois_server = tables.Column(verbose_name="WHOIS Server Override", default="(default)")
    skip = columns.BooleanColumn(verbose_name="Skip WHOIS")
    actions = columns.ActionsColumn(actions=("edit", "delete"))

    class Meta(NetBoxTable.Meta):
        model = TLDWhoisConfig
        fields = ("pk", "tld", "whois_server", "skip", "notes", "actions")
        default_columns = ("tld", "whois_server", "skip", "notes", "actions")


class ZoneValidationTable(NetBoxTable):
    zone = tables.Column(linkify=True, verbose_name="Zone")
    zone__view = tables.Column(verbose_name="View", accessor="zone__view__name", default="(default)")
    checked_at = columns.DateTimeColumn(verbose_name="Last Checked")
    overall_status = StatusBadgeColumn(verbose_name="Status")
    whois_status = StatusBadgeColumn(verbose_name="WHOIS")
    ns_status = StatusBadgeColumn(verbose_name="NS Delegation")
    resolver_status = StatusBadgeColumn(verbose_name="Resolvers")
    actions = columns.ActionsColumn(actions=("edit", "delete"))

    class Meta(NetBoxTable.Meta):
        model = ZoneValidation
        fields = (
            "pk",
            "zone",
            "zone__view",
            "checked_at",
            "overall_status",
            "whois_status",
            "ns_status",
            "resolver_status",
            "actions",
        )
        default_columns = (
            "zone",
            "zone__view",
            "checked_at",
            "overall_status",
            "whois_status",
            "ns_status",
            "resolver_status",
            "actions",
        )
