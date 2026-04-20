import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("netbox_dns", "__first__"),
        ("extras", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ZoneValidation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=None)),
                (
                    "zone",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="validation",
                        to="netbox_dns.zone",
                    ),
                ),
                ("checked_at", models.DateTimeField(blank=True, null=True, verbose_name="Last Checked")),
                (
                    "overall_status",
                    models.CharField(
                        choices=[("unknown", "Unknown"), ("pass", "Pass"), ("warning", "Warning"), ("fail", "Fail")],
                        default="unknown",
                        max_length=16,
                        verbose_name="Status",
                    ),
                ),
                (
                    "whois_status",
                    models.CharField(
                        choices=[("unknown", "Unknown"), ("pass", "Pass"), ("warning", "Warning"), ("fail", "Fail")],
                        default="unknown",
                        max_length=16,
                    ),
                ),
                ("whois_registrar", models.CharField(blank=True, max_length=256)),
                ("whois_expiry", models.DateField(blank=True, null=True, verbose_name="WHOIS Expiry")),
                ("whois_epp_statuses", models.JSONField(blank=True, default=list, verbose_name="EPP Status Codes")),
                ("whois_error", models.TextField(blank=True)),
                (
                    "ns_status",
                    models.CharField(
                        choices=[("unknown", "Unknown"), ("pass", "Pass"), ("warning", "Warning"), ("fail", "Fail")],
                        default="unknown",
                        max_length=16,
                        verbose_name="NS Delegation Status",
                    ),
                ),
                ("ns_configured", models.JSONField(blank=True, default=list, verbose_name="Configured Nameservers")),
                ("ns_delegated", models.JSONField(blank=True, default=list, verbose_name="Delegated Nameservers")),
                ("ns_missing", models.JSONField(blank=True, default=list, verbose_name="Missing from Delegation")),
                ("ns_extra", models.JSONField(blank=True, default=list, verbose_name="Extra in Delegation")),
                ("ns_error", models.TextField(blank=True)),
                (
                    "resolver_status",
                    models.CharField(
                        choices=[("unknown", "Unknown"), ("pass", "Pass"), ("warning", "Warning"), ("fail", "Fail")],
                        default="unknown",
                        max_length=16,
                        verbose_name="Resolver Status",
                    ),
                ),
                ("resolver_results", models.JSONField(blank=True, default=dict, verbose_name="Per-Nameserver Results")),
                ("resolver_error", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Zone Validation",
                "verbose_name_plural": "Zone Validations",
                "ordering": ["zone__name"],
            },
        ),
    ]
