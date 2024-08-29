from django.urls import path
from .views import (
    PharmacyByOpeningHoursAPI,
)

urlpatterns = [
    path('pharmacies/opening-hours/', PharmacyByOpeningHoursAPI.as_view(), name='pharmacies-by-opening-hours'),
]
