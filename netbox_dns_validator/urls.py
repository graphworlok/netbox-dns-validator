from django.urls import path
from . import views

urlpatterns = [
    path("", views.ZoneValidationListView.as_view(), name="zonevalidation_list"),
    path("<int:pk>/", views.ZoneValidationView.as_view(), name="zonevalidation"),
    path("<int:pk>/delete/", views.ZoneValidationDeleteView.as_view(), name="zonevalidation_delete"),

    # Trigger validation
    path("validate-view/", views.ValidateViewView.as_view(), name="validate_view"),
    path("validate-zone/<int:zone_pk>/", views.ValidateZoneView.as_view(), name="validate_zone"),
]
