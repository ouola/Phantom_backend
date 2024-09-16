import json
from datetime import datetime
from django.core.management.base import BaseCommand
from phantom_app.models import User, PurchaseHistory, Pharmacy, Mask

class Command(BaseCommand):
    help = 'Import user data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        
        with open(json_file, 'r') as f:
            data = json.load(f)
            self.import_users(data)

    def import_users(self, data):
        for entry in data:
            # Create or update user
            user, created = User.objects.get_or_create(
                name=entry['name'],
                defaults={'cash_balance': entry['cashBalance']}
            )
            if not created:
                user.cash_balance = entry['cashBalance']
                user.save()
            
            # Process purchase histories
            for purchase in entry.get('purchaseHistories', []):
                pharmacy = Pharmacy.objects.filter(name=purchase['pharmacyName']).first()
                if not pharmacy:
                    self.stdout.write(self.style.ERROR(f"Pharmacy '{purchase['pharmacyName']}' not found. Skipping purchase entry."))
                    continue

                mask = Mask.objects.filter(name=purchase['maskName'], pharmacy=pharmacy).first()
                if not mask:
                    self.stdout.write(self.style.ERROR(f"Mask '{purchase['maskName']}' not found in pharmacy '{pharmacy.name}'. Skipping purchase entry."))
                    continue

                # Parse datetime
                transaction_datetime = datetime.strptime(purchase['transactionDate'], '%Y-%m-%d %H:%M:%S')
                transaction_date = transaction_datetime.date()
                transaction_time = transaction_datetime.time()

                # Create purchase history
                PurchaseHistory.objects.create(
                    user=user,
                    pharmacy_name=purchase['pharmacyName'],
                    mask_name=purchase['maskName'],
                    transaction_amount=purchase['transactionAmount'],
                    transaction_date=transaction_date,
                    transaction_time=transaction_time
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported user data'))
