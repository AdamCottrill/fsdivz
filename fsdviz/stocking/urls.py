from django.urls import path

from .views import (PieChartMapView, PieChartMapViewLatestYear,
                    StockingEventListView, StockingEventDetailView,
                    StockingEventListLatestYear)

app_name = 'stocking'

urlpatterns = [
    path('', PieChartMapViewLatestYear, name='stocking-events'),
    path(
        'events/<int:year>/',
        PieChartMapView.as_view(),
        name='stocking-events-year'),
    path(
        'events/<lake_name>/',
        PieChartMapView.as_view(),
        name='stocking-events-lake'),
    path(
        'events/<lake_name>/<int:year>/',
        PieChartMapView.as_view(),
        name='stocking-events-lake-year'),
    path(
        'events/jurisdiction/<jurisdiction>/',
        PieChartMapView.as_view(),
        name='stocking-events-jurisdiction'),
    path(
        'events/jurisdiction/<jurisdiction>/<int:year>',
        PieChartMapView.as_view(),
        name='stocking-events-jurisdiction-year'),
    path(
        'events/<lake_name>/<int:year>/',
        PieChartMapView.as_view(),
        name='stocking-events-lake-year'),
    path(
        'events/',
        PieChartMapViewLatestYear,
        name='stocking-event-latest-year'),
    path(
        'events_list/<int:year>/',
        StockingEventListView.as_view(),
        name='stocking-event-list-year'),
    path(
        'events_list/<lake_name>/',
        StockingEventListView.as_view(),
        name='stocking-event-list-lake'),
    path(
        'events_list/<lake_name>/<int:year>/',
        StockingEventListView.as_view(),
        name='stocking-event-list-lake-year'),
    path(
        'events_list/jurisdiction/<jurisdiction>/',
        StockingEventListView.as_view(),
        name='stocking-event-list-jurisdiction'),
    path(
        'events_list/jurisdiction/<jurisdiction>/<int:year>',
        StockingEventListView.as_view(),
        name='stocking-event-list-jurisdiction-year'),
    path(
        'events_list/<lake_name>/<int:year>/',
        StockingEventListView.as_view(),
        name='stocking-event-list-lake-year'),
    path(
        'events_list/',
        StockingEventListLatestYear,
        name='stocking-event-latest-year'),
    path(
        'event_detail/<stock_id>/',
        StockingEventDetailView.as_view(),
        name='stocking-event-detail'),
]
