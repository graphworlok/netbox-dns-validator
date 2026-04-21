from django.urls import path
from . import views

urlpatterns = [
    # Zone validation results
    path("", views.ZoneValidationListView.as_view(), name="zonevalidation_list"),
    path("<int:pk>/", views.ZoneValidationView.as_view(), name="zonevalidation"),
    path("<int:pk>/delete/", views.ZoneValidationDeleteView.as_view(), name="zonevalidation_delete"),

    # Trigger validation
    path("validate-view/", views.ValidateViewView.as_view(), name="validate_view"),
    path("validate-zone/<int:zone_pk>/", views.ValidateZoneView.as_view(), name="validate_zone"),

    # TLD WHOIS config
    path("tld-config/", views.TLDWhoisConfigListView.as_view(), name="tldwhoisconfig_list"),
    path("tld-config/add/", views.TLDWhoisConfigEditView.as_view(), name="tldwhoisconfig_add"),
    path("tld-config/<int:pk>/", views.TLDWhoisConfigView.as_view(), name="tldwhoisconfig"),
    path("tld-config/<int:pk>/edit/", views.TLDWhoisConfigEditView.as_view(), name="tldwhoisconfig_edit"),
    path("tld-config/<int:pk>/delete/", views.TLDWhoisConfigDeleteView.as_view(), name="tldwhoisconfig_delete"),
]
