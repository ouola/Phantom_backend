import json
import re
from datetime import datetime, time
from django.core.management.base import BaseCommand
from phantom_app.models import Pharmacy, Mask, OpeningHour

class Command(BaseCommand):
    help = 'Import data from JSON files'

    def add_arguments(self, parser):
        parser.add_argument('data_file', type=str, help='Path to the JSON file to import')

    def handle(self, *args, **options):
        data_file = options['data_file']
        with open(data_file, 'r') as file:
            data = json.load(file)
        self.import_pharmacies(data)

    def import_pharmacies(self, data):
        for entry in data:
            pharmacy, created = Pharmacy.objects.get_or_create(
                name=entry['name'],
                defaults={
                    'cash_balance': entry['cashBalance'],
                    'opening_hours': entry['openingHours']
                }
            )
            if created:
                print(f"Created new pharmacy: {pharmacy.name}")
            else:
                print(f"Pharmacy already exists: {pharmacy.name}")

            # 處理開放時間
            self.import_opening_hours(pharmacy, entry['openingHours'])

            # 處理面罩
            self.import_masks(pharmacy, entry.get('masks', []))

    def import_opening_hours(self, pharmacy, opening_hours):
        time_slots = self.parse_opening_hours(opening_hours)
        
        # 刪除舊的開放時間紀錄
        OpeningHour.objects.filter(pharmacy=pharmacy).delete()

        for day_of_week, (start_time, end_time) in time_slots.items():
            OpeningHour.objects.create(
                pharmacy=pharmacy,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )
            print(f"Added opening hours for {pharmacy.name} on {day_of_week}")

    def import_masks(self, pharmacy, masks):
        # 刪除舊的面罩紀錄
        Mask.objects.filter(pharmacy=pharmacy).delete()

        for mask_data in masks:
            Mask.objects.create(
                pharmacy=pharmacy,
                name=mask_data['name'],
                price=mask_data['price']
            )
            print(f"Added mask '{mask_data['name']}' to pharmacy {pharmacy.name}")

    def parse_opening_hours(self, opening_hours):
        time_slots = {}

        segments = opening_hours.split('/')

        for segment in segments:
            segment = segment.strip()

            # 確保 segment 包含空格，以分割天數和時間範圍
            if ' ' not in segment:
                continue

            # 分割天數和時間範圍
            parts = segment.split(' ', 1)
            if len(parts) < 2:
                continue

            days, times = parts
            days = days.strip()
            times = times.strip()

            # 匹配時間範圍
            time_pattern = re.compile(
                r'(?P<days>[A-Za-z, -]+) (?P<start_time>\d{2}:\d{2}) - (?P<end_time>\d{2}:\d{2})'
            )
            time_match = time_pattern.match(segment)
            if not time_match:
                self.stdout.write(self.style.ERROR(f"Invalid time format in opening hours: {opening_hours}"))
                continue

            days_str = time_match.group('days').strip()
            start_time_str = time_match.group('start_time').strip()
            end_time_str = time_match.group('end_time').strip()

            try:
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                end_time = datetime.strptime(end_time_str, '%H:%M').time()

                # 處理跨日情況
                time_ranges = self.handle_time_over_midnight(start_time, end_time)

            except ValueError as e:
                self.stdout.write(self.style.ERROR(f"Invalid time format in opening hours: {opening_hours}. Error: {e}"))
                continue

            for day in self.expand_days(days_str):
                if day:
                    if day in time_slots:
                        # 如果已有該天的時間範圍，取最早的開始時間和最晚的結束時間
                        existing_start_str, existing_end_str = time_slots[day]
                        existing_start = datetime.strptime(existing_start_str, '%H:%M').time()
                        existing_end = datetime.strptime(existing_end_str, '%H:%M').time()
                        new_start = min(time_ranges[0][0], existing_start)
                        new_end = max(time_ranges[-1][1], existing_end)
                        time_slots[day] = (new_start.strftime('%H:%M'), new_end.strftime('%H:%M'))
                    else:
                        time_slots[day] = (
                            time_ranges[0][0].strftime('%H:%M'),
                            time_ranges[-1][1].strftime('%H:%M')
                        )

        return time_slots

    def expand_days(self, days):
        days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        expanded_days = set()
        
        if '-' in days:
            start_day, end_day = [d.strip() for d in days.split('-')]
            start_index = days_of_week.index(start_day)
            end_index = days_of_week.index(end_day)
            week_days = days_of_week[start_index:end_index + 1]
            expanded_days.update(week_days)
        else:
            for d in days.split(','):
                d = d.strip()
                if d in days_of_week:
                    expanded_days.add(d)
                    
        return expanded_days
        
    def handle_time_over_midnight(self, start_time, end_time):
        # 這個方法應返回一個包含兩個元組的列表，分別為開始和結束時間
        if start_time > end_time:
            return [
                (start_time, time(23, 59)), 
                (time(0, 0), end_time)
            ]
        else:
            return [
                (start_time, end_time)
            ]
