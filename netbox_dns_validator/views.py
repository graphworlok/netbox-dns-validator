import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from netbox.views import generic

from .filters import ZoneValidationFilterSet
from .forms import TLDWhoisConfigForm, ValidateViewForm, ZoneValidationFilterForm
from .models import TLDWhoisConfig, ZoneValidation
from .tables import TLDWhoisConfigTable, ZoneValidationTable


# ---------------------------------------------------------------------------
# TLD WHOIS Config CRUD
# ---------------------------------------------------------------------------

class TLDWhoisConfigListView(generic.ObjectListView):
    queryset = TLDWhoisConfig.objects.all()
    table = TLDWhoisConfigTable


class TLDWhoisConfigView(generic.ObjectView):
    queryset = TLDWhoisConfig.objects.all()


class TLDWhoisConfigEditView(generic.ObjectEditView):
    queryset = TLDWhoisConfig.objects.all()
    form = TLDWhoisConfigForm


class TLDWhoisConfigDeleteView(generic.ObjectDeleteView):
    queryset = TLDWhoisConfig.objects.all()

logger = logging.getLogger(__name__)


class ZoneValidationListView(generic.ObjectListView):
    queryset = ZoneValidation.objects.select_related("zone", "zone__view").order_by("zone__name")
    table = ZoneValidationTable
    filterset = ZoneValidationFilterSet
    filterset_form = ZoneValidationFilterForm
    template_name = "netbox_dns_validator/zone_validation_list.html"


class ZoneValidationView(generic.ObjectView):
    queryset = ZoneValidation.objects.select_related("zone", "zone__view")
    template_name = "netbox_dns_validator/zone_validation_detail.html"


class ZoneValidationDeleteView(generic.ObjectDeleteView):
    queryset = ZoneValidation.objects.all()


class ValidateZoneView(View):
    """POST: run all checks for a single zone and redirect to its detail page."""

    def post(self, request, zone_pk):
        from netbox_dns.models import Zone
        from .validators.runner import validate_zone

        zone = get_object_or_404(Zone, pk=zone_pk)
        try:
            validation = validate_zone(zone)
            messages.success(request, f"Validation complete for {zone.name}.")
            return redirect(validation.get_absolute_url())
        except Exception as exc:
            logger.exception("Validation failed for zone %s", zone.name)
            messages.error(request, f"Validation failed: {exc}")
            return redirect("plugins:netbox_dns_validator:zonevalidation_list")


class ValidateViewView(View):
    """GET: show view-picker form. POST: validate all zones in the chosen view."""

    template_name = "netbox_dns_validator/validate_view.html"

    def get(self, request):
        form = ValidateViewForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        from netbox_dns.models import Zone, View
        from .validators.runner import validate_zone

        form = ValidateViewForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        view_name = form.cleaned_data["view"]

        if view_name == "__default__":
            zones = Zone.objects.filter(view__isnull=True)
        else:
            try:
                view = View.objects.get(name=view_name)
                zones = Zone.objects.filter(view=view)
            except View.DoesNotExist:
                messages.error(request, f"View '{view_name}' not found.")
                return render(request, self.template_name, {"form": form})

        ok = fail = 0
        for zone in zones:
            try:
                validate_zone(zone)
                ok += 1
            except Exception as exc:
                logger.warning("Validation failed for %s: %s", zone.name, exc)
                fail += 1

        if fail:
            messages.warning(request, f"Validated {ok} zones; {fail} failed — check logs.")
        else:
            messages.success(request, f"Validated {ok} zones in view '{view_name}'.")

        return redirect("plugins:netbox_dns_validator:zonevalidation_list")
