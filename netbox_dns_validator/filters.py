import django_filters
from django.db.models import Q

from .models import ZoneValidation
from .choices import ValidationStatusChoices


class ZoneValidationFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(method="search", label="Search")

    overall_status = django_filters.MultipleChoiceFilter(
        choices=ValidationStatusChoices,
        label="Overall Status",
    )
    whois_status = django_filters.MultipleChoiceFilter(
        choices=ValidationStatusChoices,
        label="WHOIS Status",
    )
    ns_status = django_filters.MultipleChoiceFilter(
        choices=ValidationStatusChoices,
        label="NS Delegation Status",
    )
    resolver_status = django_filters.MultipleChoiceFilter(
        choices=ValidationStatusChoices,
        label="Resolver Status",
    )

    # Filter by netbox-dns view name
    view = django_filters.CharFilter(
        field_name="zone__view__name",
        lookup_expr="iexact",
        label="View",
    )

    class Meta:
        model = ZoneValidation
        fields = ["overall_status", "whois_status", "ns_status", "resolver_status"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(zone__name__icontains=value) | Q(whois_registrar__icontains=value)
        )
