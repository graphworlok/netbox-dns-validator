from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm

from .models import TLDWhoisConfig, ZoneValidation
from .choices import ValidationStatusChoices


class TLDWhoisConfigForm(NetBoxModelForm):
    fieldsets = (
        ("TLD Override", ("tld", "whois_server", "skip", "notes")),
    )

    class Meta:
        model = TLDWhoisConfig
        fields = ("tld", "whois_server", "skip", "notes")
        help_texts = {
            "tld": "Suffix without leading dot — use multi-part form for second-level TLDs, e.g. <code>co.uk</code> or <code>com.au</code>",
        }


class ZoneValidationFilterForm(NetBoxModelFilterSetForm):
    model = ZoneValidation
    fieldsets = (
        (None, ("q", "view", "overall_status", "whois_status", "ns_status", "resolver_status")),
    )

    view = forms.CharField(required=False, label="netbox-dns View")
    overall_status = forms.MultipleChoiceField(
        choices=ValidationStatusChoices,
        required=False,
        label="Overall Status",
    )
    whois_status = forms.MultipleChoiceField(
        choices=ValidationStatusChoices,
        required=False,
        label="WHOIS Status",
    )
    ns_status = forms.MultipleChoiceField(
        choices=ValidationStatusChoices,
        required=False,
        label="NS Delegation Status",
    )
    resolver_status = forms.MultipleChoiceField(
        choices=ValidationStatusChoices,
        required=False,
        label="Resolver Status",
    )


class ValidateViewForm(forms.Form):
    """Selects a netbox-dns view to validate all zones within it."""

    view = forms.ChoiceField(label="netbox-dns View", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from netbox_dns.models import View
            choices = [("", "--- select ---")] + [
                (v.name, v.name) for v in View.objects.order_by("name")
            ]
            # Add a sentinel for zones with no view assigned
            choices.append(("__default__", "(default view)"))
        except Exception:
            choices = [("", "netbox-dns not available")]
        self.fields["view"].choices = choices
