from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_dns_validator", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="zonevalidation",
            name="whois_server_used",
            field=models.CharField(
                blank=True,
                max_length=256,
                verbose_name="WHOIS Server",
                help_text="WHOIS server queried (blank = python-whois default for this TLD)",
            ),
        ),
    ]
