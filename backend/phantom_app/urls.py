from django.urls import path
from .views import (
    PharmacyByOpeningHoursAPI,
    MasksByPharmacyAPI,
)

urlpatterns = [
    path('pharmacies/opening-hours/', PharmacyByOpeningHoursAPI.as_view(), name='pharmacies-by-opening-hours'),
    path('pharmacies/masks/', MasksByPharmacyAPI.as_view(), name='masks-by-pharmacy'),
]
