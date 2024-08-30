from django.urls import path
from .views import (
    PharmacyByOpeningHoursAPIView,
    MasksByPharmacyAPIView,
    PharmaciesByMaskCountAPIView,
    TopUsersByTransactionAPIView,
)

urlpatterns = [
    path('pharmacies/opening-hours/', PharmacyByOpeningHoursAPIView.as_view(), name='pharmacies-by-opening-hours'),
    path('pharmacies/masks/', MasksByPharmacyAPIView.as_view(), name='masks-by-pharmacy'),
    path('pharmacies/mask-count/', PharmaciesByMaskCountAPIView.as_view(), name='pharmacies_by_mask_count'),
    path('users/top-transactions/', TopUsersByTransactionAPIView.as_view(), name='top_transactions'),

]
