"""Views for the api for our common models

The veiws in this file should all be publicly available as readonly.

"""

from django.conf import settings
from django.db.models import Count, F, Q, Sum

from django.contrib.postgres.aggregates import StringAgg
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer


from fsdviz.stocking.models import LifeStage, Condition, StockingMethod, StockingEvent
from fsdviz.stocking.filters import StockingEventFilter

from .serializers import (
    LifeStageSerializer,
    ConditionSerializer,
    StockingMethodSerializer,
    StockingEventSerializer,
    StockingEventFastSerializer,
    StockingEventXlsxSerializer,
)


from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer


class StockingEvent2xlsxViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    """This view set will export the stockign data to excel in the same
    format as the data submission template."""

    queryset = StockingEvent.objects.all()
    serializer_class = StockingEventXlsxSerializer
    filterset_class = StockingEventFilter
    # queryset = LifeStage.objects.all()
    # serializer_class = LifeStageSerializer
    renderer_classes = (XLSXRenderer, JSONRenderer)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filename = "glfsd_export.xlsx"

    column_header = {
        "height": 15,
        "style": {
            "fill": {
                "fill_type": "solid",
                "start_color": "00C0C0C0",
            },
            "alignment": {
                "horizontal": "center",
                "vertical": "center",
                "wrapText": True,
                "shrink_to_fit": True,
            },
            "font": {
                "name": "Calibri",
                "size": 12,
                "bold": True,
            },
        },
    }
    body = {
        "style": {
            "font": {
                "name": "Calibri",
                "size": 11,
                "bold": False,
            }
        },
        "height": 15,
    }

    def get_queryset(self):

        field_aliases = {
            "glfsd_stock_id": F("stock_id"),
            "agency_code": F("agency__abbrev"),
            "_lake": F("jurisdiction__lake__abbrev"),
            "state_prov": F("jurisdiction__stateprov__abbrev"),
            "manUnit": F("management_unit__label"),
            "grid_10min": F("grid_10__grid"),
            "location_primary": F("st_site"),
            "location_secondary": F("site"),
            "latitude": F("dd_lat"),
            "longitude": F("dd_lon"),
            "stock_method": F("stocking_method__stk_meth"),
            "species_code": F("species__abbrev"),
            "_strain": F("strain_raw__strain__strain_code"),
            "yearclass": F("year_class"),
            "life_stage": F("lifestage__abbrev"),
            "age_months": F("agemonth"),
            "_clip": F("clip_code__clip_code"),
            "phys_chem_mark": F("physchem_marks"),
            "cwt_number": F("tag_no"),
            "tag_retention": F("tag_ret"),
            "mean_length_mm": F("length"),
            "total_weight_kg": F("weight"),
            "stocking_mortality": F("condition__condition"),
            "lot_code": F("lotcode"),
            "hatchery_abbrev": F("hatchery__abbrev"),
            "number_stocked": F("no_stocked"),
            "tag_type": StringAgg("fish_tags__tag_code", ""),
        }

        fields = [
            "glfsd_stock_id",
            "agency_stock_id",
            "agency_code",
            "_lake",
            "state_prov",
            "manUnit",
            "grid_10min",
            "location_primary",
            "location_secondary",
            "latitude",
            "longitude",
            "year",
            "month",
            "day",
            "stock_method",
            "species_code",
            "_strain",
            "yearclass",
            "life_stage",
            "age_months",
            "_clip",
            "clip_efficiency",
            "phys_chem_mark",
            "tag_type",
            "cwt_number",
            "tag_retention",
            "mean_length_mm",
            "total_weight_kg",
            "stocking_mortality",
            "lot_code",
            "hatchery_abbrev",
            "number_stocked",
            "notes",
        ]

        queryset = (
            StockingEvent.objects.select_related(
                "jurisdiction",
                "agency",
                "species",
                "strain_raw__strain",
                "lifestage",
                "condition",
                "grid_10",
                "stocking_method",
                "hatchery",
                "fish_tags",
                "jurisdiction__lake",
                "jurisdiction__stateprov",
            )
            .order_by("-year", "stock_id")
            .annotate(**field_aliases)
            .values(*fields)
        )

        filtered = StockingEventFilter(self.request.GET, queryset=queryset).qs.values(
            *fields
        )

        return filtered


class LifeStageViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = LifeStage.objects.all()
    serializer_class = LifeStageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ConditionViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer


class StockingMethodViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = StockingMethod.objects.all()
    serializer_class = StockingMethodSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class StockingEventViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = StockingEventSerializer
    filterset_class = StockingEventFilter
    lookup_field = "stock_id"
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):

        queryset = StockingEvent.objects.all()
        queryset = queryset.select_related(
            "agency",
            "jurisdiction",
            "jurisdiction__stateprov",
            "jurisdiction__lake",
            "species",
            "lifestage",
            "grid_10",
            "grid_10__lake",
            "latlong_flag",
            "strain_raw__strain",
            "stocking_method",
        )

        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        # finally django-filter
        filtered_list = StockingEventFilter(self.request.GET, queryset=queryset)

        return filtered_list.qs[:100]


class StockingEventMapListView(generics.ListAPIView):
    """A list view of stocking events. Events are aggregated to minimize
    the number of records returned.  Only fields needed to create maps
    and associated filter widgets are included.

    Filters available in other api views are not used in is view.

    NOTE: we could consider changing the level of aggregation
    depending on the spatial scale of the map this is called from. -
    No need for lat-lon at the basin level.

    """

    serializer_class = StockingEventFastSerializer
    filterset_class = StockingEventFilter
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(queryset)

    def get_queryset(self):

        # get any url parameters:
        upload_event = self.kwargs.get("upload_event_slug")

        # count our events and sum the yreq_stocked, give each field
        # that is from a child table as a simple label
        metrics = {
            "stateprov": F("jurisdiction__stateprov__abbrev"),
            "lake": F("jurisdiction__lake__abbrev"),
            "jurisdiction_slug": F("jurisdiction__slug"),
            "man_unit": F("management_unit__slug"),
            "grid10": F("grid_10__slug"),
            "stk_method": F("stocking_method__stk_meth"),
            "life_stage": F("lifestage__abbrev"),
            "agency_abbrev": F("agency__abbrev"),
            "species_name": F("species__abbrev"),
            "strain": F("strain_raw__strain__strain_label"),
        }

        aggregation_metrics = {
            "events": Count("id"),
            "yreq": Sum("yreq_stocked"),
            "total_stocked": Sum("no_stocked"),
        }

        queryset = StockingEvent.objects.select_related(
            "species",
            "lifestage",
            "jurisdiction",
            "jurisdiction__lake",
            "jurisdiction__stateprov",
            "grid_10",
            "management_unit",
            "agency",
            "strain_raw__strain",
            "stocking_method",
        ).prefetch_related(
            "species",
            "lifestage",
            "jurisdiction",
            "jurisdiction__lake",
            "jurisdiction__stateprov",
            "grid_10",
            "management_unit",
            "agency",
            "strain_raw__strain",
            "stocking_method",
        )

        if upload_event:
            queryset = queryset.filter(upload_event__slug=upload_event)

        # finally django-filter
        filtered_list = StockingEventFilter(self.request.GET, queryset=queryset)

        qs = (
            filtered_list.qs.annotate(**metrics)
            .values(
                "dd_lat",
                "dd_lon",
                "month",
                "lake",
                "jurisdiction_slug",
                "man_unit",
                "stateprov",
                "grid10",
                "life_stage",
                "stk_method",
                "agency_abbrev",
                "species_name",
                "strain",
                "year_class",
                "mark",
            )
            .order_by()
            .annotate(**aggregation_metrics)
        )

        return qs


class StockingEventListAPIView(APIView):
    """A list view of individual stocking events. This view is meant to be
    called from find_events view and should always return a reasonable
    subset of the database (say less than 5000 records?).

    query parmeters are parsed from the url and used to filter the
    returned queryest.

    To maximize performance, this view does not use a serializer and
    instead returns just the values from the queryset was recommended here:

    https://www.dabapps.com/blog/api-performance-profiling-django-rest-framework/

    Note: this is something we might want to consider for our other views too.

    TODO: when slug is available for strain, use it. for now we will
    build it on the front end.

    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):

        field_aliases = {
            "agency_code": F("agency__abbrev"),
            "species_code": F("species__abbrev"),
            "strain": F("strain_raw__strain__strain_code"),
            "grid10": F("grid_10__slug"),
            "lifestage_code": F("lifestage__abbrev"),
            "stockingMethod": F("stocking_method__stk_meth"),
            "jurisdiction_code": F("jurisdiction__slug"),
            "lake": F("jurisdiction__lake__abbrev"),
            "stateProv": F("jurisdiction__stateprov__abbrev"),
        }

        fields = [
            "stock_id",
            "lake",
            "jurisdiction_code",
            "stateProv",
            "grid10",
            "dd_lat",
            "dd_lon",
            "st_site",
            "year",
            "date",
            "month",
            "mark",
            "year_class",
            "agency_code",
            "species_code",
            "strain",
            "lifestage_code",
            "stockingMethod",
            "no_stocked",
            "yreq_stocked",
        ]

        queryset = StockingEvent.objects.select_related(
            "jurisdiction",
            "agency",
            "species",
            "strain",
            "lifestage",
            "grid_10",
            "stocking_method",
            "jurisdiction__lake",
            "jurisdiction__stateprov",
        ).annotate(**field_aliases)

        filtered = StockingEventFilter(request.GET, queryset=queryset).qs.values(
            *fields
        )

        maxEvents = settings.MAX_FILTERED_EVENT_COUNT

        return Response(filtered[:maxEvents])


class StockingEventLookUpsAPIView(APIView):
    """This api endpoint will return a json object that contains lookups
    for the stocking model objects needed to label stocking events.
    The api endpoint that returns the stocking events contains only
    id's or slugs form most fields to that the payload is compact and
    the javscript processing on the front end is as efficient as
    possible.  This endpoint provides the lookup values so that the
    stocking method 'b' can be displayed as "boat, offshore
    stocking".  Originally, this information was collected through
    separate api calls for each attribute.

    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):

        lifestages = LifeStage.objects.values("abbrev", "description")
        stockingmethods = StockingMethod.objects.values("stk_meth", "description")

        lookups = {
            "stockingmethods": list(stockingmethods),
            "lifestages": list(lifestages),
        }

        return Response(lookups)


class CWTEventListAPIView(APIView):
    """A list view of individual cwt stocking events, inlcuding
    attributes of the associated cwt.

    Query parmeters are parsed from the url and used to filter the
    returned queryset.  See the swagger documentation enpoint for the
    complete list of available filters.

    To maximize performance, this view does not use a serializer and
    instead returns just the values from the queryset as recommended here:

    https://www.dabapps.com/blog/api-performance-profiling-django-rest-framework/

    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):

        field_aliases = {
            "cwt_number": F("cwt_series__cwt__cwt_number"),
            "seq_lower": F("cwt_series__seq_lower"),
            "seq_upper": F("cwt_series__seq_upper"),
            "tag_type": F("cwt_series__cwt__tag_type"),
            "manufacturer": F("cwt_series__cwt__manufacturer"),
            "tag_reused": F("cwt_series__cwt__tag_reused"),
            "multiple_lakes": F("cwt_series__cwt__multiple_lakes"),
            "multiple_species": F("cwt_series__cwt__multiple_species"),
            "multiple_strains": F("cwt_series__cwt__multiple_strains"),
            "multiple_yearclasses": F("cwt_series__cwt__multiple_yearclasses"),
            "multiple_agencies": F("cwt_series__cwt__multiple_agencies"),
            "agency_code": F("agency__abbrev"),
            "lake": F("jurisdiction__lake__abbrev"),
            "state": F("jurisdiction__stateprov__abbrev"),
            "jurisd": F("jurisdiction__slug"),
            "man_unit": F("management_unit__label"),
            "grid10": F("grid_10__grid"),
            "latitude": F("_dd_lat"),
            "longitude": F("_dd_lon"),
            "primary_location": F("site"),
            "secondary_location": F("st_site"),
            "spc": F("species__abbrev"),
            "strain": F("strain_raw__strain__strain_label"),
            "clipcode": F("clip_code__clip_code"),
            "stage": F("lifestage__description"),
            "method": F("stocking_method__description"),
        }

        # use our shorter field names in the list of fields to select:
        fields = [
            "cwt_number",
            "tag_type",
            "seq_lower",
            "seq_upper",
            "manufacturer",
            "tag_reused",
            "multiple_lakes",
            "multiple_species",
            "multiple_strains",
            "multiple_yearclasses",
            "multiple_agencies",
            "stock_id",
            "agency_stock_id",
            "agency_code",
            "lake",
            "state",
            "jurisd",
            "man_unit",
            "grid10",
            "primary_location",
            "secondary_location",
            "latitude",
            "longitude",
            "year",
            "month",
            "day",
            "spc",
            "strain",
            "year_class",
            "mark",
            "clipcode",
            "stage",
            "method",
            "no_stocked",
        ]

        related_tables = [
            "cwt",
            "cwt_series",
            "agency",
            "species",
            "strain_raw",
            "strain_raw__strain",
            "lifestage",
            "stocking_method",
            "jurisdiction__lake",
            "jurisdiction__stateprov",
            "jurisdiction",
            "grid_10",
        ]

        queryset = StockingEvent.objects.filter(
            cwt_series__cwt__cwt_number__isnull=False
        ).select_related(*related_tables)

        filtered_qs = StockingEventFilter(self.request.GET, queryset=queryset).qs

        values = filtered_qs.annotate(**field_aliases).values(*fields)
        maxEvents = settings.MAX_FILTERED_EVENT_COUNT
        return Response(values[:maxEvents])
