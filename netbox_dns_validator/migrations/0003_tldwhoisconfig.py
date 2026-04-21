from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_dns_validator", "0002_whois_server_used"),
    ]

    operations = [
        migrations.CreateModel(
            name="TLDWhoisConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=None)),
                (
                    "tld",
                    models.CharField(
                        max_length=64,
                        unique=True,
                        verbose_name="TLD Suffix",
                        help_text="Suffix without leading dot, e.g. 'au' or 'co.uk'",
                    ),
                ),
                (
                    "whois_server",
                    models.CharField(
                        blank=True,
                        max_length=256,
                        verbose_name="WHOIS Server",
                        help_text="Override WHOIS server hostname (leave blank to use python-whois default)",
                    ),
                ),
                (
                    "skip",
                    models.BooleanField(
                        default=False,
                        verbose_name="Skip WHOIS",
                        help_text="Do not attempt WHOIS for this TLD — result will show as Unknown",
                    ),
                ),
                ("notes", models.TextField(blank=True, help_text="Optional note explaining this override")),
            ],
            options={
                "verbose_name": "TLD WHOIS Config",
                "verbose_name_plural": "TLD WHOIS Configs",
                "ordering": ["tld"],
            },
        ),
    ]
