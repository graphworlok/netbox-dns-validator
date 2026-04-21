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
        (
            "Configuration",
            (
                PluginMenuItem(
                    link="plugins:netbox_dns_validator:tldwhoisconfig_list",
                    link_text="TLD WHOIS Config",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_dns_validator:tldwhoisconfig_add",
                            title="Add TLD Override",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                        ),
                    ),
                ),
            ),
        ),
    ),
    icon_class="mdi mdi-dns",
)
