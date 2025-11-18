# django_app/production/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Production & Rendement
    path("api/production/timeseries/", views.api_production_timeseries, name="api_production_timeseries"),
    path("api/production/top/", views.api_top_producers, name="api_top_producers"),
    path("api/production/vs-price/", views.api_production_vs_price, name="api_production_vs_price"),
    path("api/production/fertilizer-vs-production/", views.api_fertilizer_vs_production, name="api_fertilizer_vs_production"),

    # Prix & Economie
    path("api/price/timeseries/", views.api_price_timeseries, name="api_price_timeseries"),
    path("api/price/by-country/", views.api_price_by_country, name="api_price_by_country"),
    path("api/fdi/stacked/", views.api_fdi_stacked, name="api_fdi_stacked"),
    path("api/price/boxplot/", views.api_price_boxplot, name="api_price_boxplot"),

    # Ressources & Main-d'oeuvre
    path("api/land/share/", views.api_land_share, name="api_land_share"),
    path("api/employment/timeseries/", views.api_employment_timeseries, name="api_employment_timeseries"),
    path("api/employment/vs-production/", views.api_employment_vs_production, name="api_employment_vs_production"),
]
