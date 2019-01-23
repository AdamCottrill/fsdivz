"""
Factories for the models in the stocking application - lifestage, condition,
stocking event, etc.

"""

from datetime import datetime
import factory

from django.contrib.gis.geos import GEOSGeometry

#import common.models as common
from ..stocking.models import (LifeStage, Condition, StockingMethod,
                               StockingEvent)

from .common_factories import (LakeFactory, AgencyFactory, SpeciesFactory,
                               StrainRawFactory, StateProvinceFactory,
                               Grid10Factory, LatLonFlagFactory)


class LifeStageFactory(factory.DjangoModelFactory):
    """
    A factory for LatLonFlag objects.
    """

    class Meta:
        model = LifeStage

    abbrev = 'y'
    description = 'Yearling'


class ConditionFactory(factory.DjangoModelFactory):
    """
    A factory for Condition objects.
    """

    class Meta:
        model = Condition

    condition = 1
    description = '<1% mortality observed, "excellent"'


class StockingMethodFactory(factory.DjangoModelFactory):
    """
    A factory for StockingMethod objects.
    """

    class Meta:
        model = StockingMethod

    stk_meth = 'b'
    description = 'boat, offshore stocking'


class StockingEventFactory(factory.DjangoModelFactory):
    """
    A factory for StockingEvent objects.
    """

    class Meta:
        model = StockingEvent


    #foreign keys:
    species = factory.SubFactory(SpeciesFactory)
    strain_raw = factory.SubFactory(StrainRawFactory)
    agency = factory.SubFactory(AgencyFactory)
    lake = factory.SubFactory(LakeFactory)
    grid_10 = factory.SubFactory(Grid10Factory)
    stateprov = factory.SubFactory(StateProvinceFactory)
    stocking_method = factory.SubFactory(StockingMethodFactory)
    lifestage = factory.SubFactory(LifeStageFactory)
    condition = factory.SubFactory(ConditionFactory)

    latlong_flag = factory.SubFactory(LatLonFlagFactory)

    #event attributes:
    stock_id = 'USFWS-1234'

    date = datetime(2016, 4, 20)
    day = 20
    month = 4
    year = 2016
    site = 'The Reef'

    dd_lat = 45.5
    dd_lon = -81.25

    geom = GEOSGeometry('POINT(-81.25 45.5)', srid=4326)

    no_stocked = 15000
    yreq_stocked = 15000
    year_class = 2015
    agemonth = 16

    clipa = '14'
    mark = 'RPLV'