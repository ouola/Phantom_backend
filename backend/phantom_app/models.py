from django.db import models
from django.utils import timezone

class Pharmacy(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2)
    opening_hours = models.TextField()

    def __str__(self):
        return self.name
    
class Mask(models.Model):
    # 連接至Pharmacy
    pharmacy = models.ForeignKey(Pharmacy, related_name='masks',on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f" {self.pharmacy.name} - {self.name}"
    
class User(models.Model):
    name = models.CharField(max_length=255)
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class PurchaseHistory(models.Model):
    user = models.ForeignKey(User, related_name='purchases', on_delete=models.CASCADE)
    pharmacy = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.name} - {self.mask_name} - {self.transaction_amount} - {self.transaction_date}"