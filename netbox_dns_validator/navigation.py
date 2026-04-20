from netbox.plugins.navigation import PluginMenu, PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu = PluginMenu(
    label="DNS Validator",
    groups=(
        (
            "Validation",
            (
                PluginMenuItem(
                    link="plugins:netbox_dns_validator:zonevalidation_list",
                    link_text="Zone Results",
                ),
                PluginMenuItem(
                    link="plugins:netbox_dns_validator:validate_view",
                    link_text="Validate a View",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_dns_validator:validate_view",
                            title="Run Validation",
                            icon_class="mdi mdi-play",
                            color=ButtonColorChoices.BLUE,
                        ),
                    ),
                ),
            ),
        ),
    ),
    icon_class="mdi mdi-dns",
)
