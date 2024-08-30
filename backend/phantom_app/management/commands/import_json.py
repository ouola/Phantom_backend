import json
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from phantom_app.models import User, Pharmacy, Mask, PurchaseHistory
from datetime import datetime

class Command(BaseCommand):
    help = 'Import data from JSON files into the database'

    def add_arguments(self, parser):
        parser.add_argument('model', type=str, choices=['users', 'pharmacies'], help='Specify the model to import data into.')
        parser.add_argument('file_path', type=str, help='The path to the JSON file.')

    def handle(self, *args, **options):
        model = options['model']
        file_path = options['file_path']
        
        with open(file_path, 'r') as file:
            data = json.load(file)

        if model == 'users':
            self.import_users(data)
        elif model == 'pharmacies':
            self.import_pharmacies(data)

    def import_users(self, data):
        for entry in data:
            user, created = User.objects.get_or_create(
                name=entry['name'],
                cash_balance=entry['cashBalance']
            )
            
            # 檢查 purchaseHistory 鍵是否存在
            if 'purchaseHistories' not in entry:
                self.stdout.write(self.style.WARNING(f"User {entry['name']} has no purchase history. Skipping."))
                continue

            for purchase in entry['purchaseHistories']:
                pharmacy = Pharmacy.objects.get(name=purchase['pharmacyName'])

                transaction_date = make_aware(datetime.strptime(purchase['transactionDate'], '%Y-%m-%d %H:%M:%S'))

                PurchaseHistory.objects.get_or_create(
                    user=user,
                    pharmacy=pharmacy,
                    mask_name=purchase['maskName'],
                    transaction_amount=purchase['transactionAmount'],
                    transaction_date=transaction_date,
                )

    def import_pharmacies(self, data):
        for entry in data:
            try:
                # 使用 get_or_create 來獲取或創建藥局
                pharmacy, created = Pharmacy.objects.get_or_create(
                    name=entry['name'],
                    defaults={
                        'cash_balance': entry['cashBalance'],
                        'opening_hours': entry['openingHours']
                    }
                )
            except IntegrityError:
                # 如果遇到 IntegrityError，跳過當前條目或進行其他處理
                print(f"Pharmacy '{entry['name']}' already exists. Skipping.")
                continue

            for mask_entry in entry['masks']:
                try:
                    # 使用 get_or_create 來獲取或創建口罩
                    mask, mask_created = Mask.objects.get_or_create(
                        name=mask_entry['name'],
                        pharmacy=pharmacy,
                        defaults={'price': mask_entry['price']}
                    )
                except IntegrityError:
                    # 如果遇到 IntegrityError，跳過當前條目或進行其他處理
                    print(f"Mask '{mask_entry['name']}' already exists for pharmacy '{pharmacy.name}'. Skipping.")
                    continue

                # 如果找到現有的 mask 並且價格有變動，則更新價格
                if not mask_created:
                    if mask.price != mask_entry['price']:
                        mask.price = mask_entry['price']
                        mask.save()
