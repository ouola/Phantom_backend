from django.db import models

class Pharmacy(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2)
    opening_hours = models.TextField()  # 儲存原始的開放時間格式

    def __str__(self):
        return self.name

class Mask(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, related_name='masks', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.pharmacy.name} - {self.name}"

class User(models.Model):
    name = models.CharField(max_length=255)
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class PurchaseHistory(models.Model):
    user = models.ForeignKey(User, related_name='purchase_histories', on_delete=models.CASCADE)
    pharmacy_name = models.CharField(max_length=255)
    mask_name = models.CharField(max_length=255)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateField()  # 儲存日期
    transaction_time = models.TimeField()  # 儲存時間
    day_of_week = models.CharField(max_length=10, blank=True)  # 儲存星期幾

    def save(self, *args, **kwargs):
        # 自動生成星期幾
        self.day_of_week = self.transaction_date.strftime('%A')
        super().save(*args, **kwargs)

class OpeningHour(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, related_name='opening_hours_records', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=255)  # 例如：'Monday', 'Tuesday'
    start_time = models.TimeField()  # 開始時間
    end_time = models.TimeField()    # 結束時間

    def __str__(self):
        return f"{self.pharmacy.name} - {self.day_of_week} ({self.start_time} - {self.end_time})"
