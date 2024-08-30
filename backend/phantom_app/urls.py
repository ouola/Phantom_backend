from django.urls import path
from .views import (
    PharmacyByOpeningHoursAPIView,
    MasksByPharmacyAPIView,
    PharmaciesByMaskCountAPIView,
    TopUsersByTransactionAPIView,
    TotalMasksAndTransactionValueAPIView,
    SearchAPIView,
    PurchaseMaskAPIView
)

urlpatterns = [
    path('pharmacies/opening-hours/', PharmacyByOpeningHoursAPIView.as_view(), name='pharmacies-by-opening-hours'),
    path('pharmacies/masks/', MasksByPharmacyAPIView.as_view(), name='masks-by-pharmacy'),
    path('pharmacies/mask-count/', PharmaciesByMaskCountAPIView.as_view(), name='pharmacies_by_mask_count'),
    path('users/top-transactions/', TopUsersByTransactionAPIView.as_view(), name='top_transactions'),
    path('transactions/total/', TotalMasksAndTransactionValueAPIView.as_view(), name='total-masks-and-transaction-value'),
    path('search/', SearchAPIView.as_view(), name='search'),
    path('purchase-mask/', PurchaseMaskAPIView.as_view(), name='purchase-mask'),
]
