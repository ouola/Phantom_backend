from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Pharmacy
import re
from datetime import datetime

class PharmacyByOpeningHoursAPI(APIView):
    def get(self, request):
        weekday = request.query_params.get('weekday')
        time = request.query_params.get('time')

        if not weekday or not time:
            return Response({'error': 'Weekday and time parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 轉換時間使可運算
        try:
            query_time = datetime.strptime(time, '%H:%M').time()
        except ValueError:
            return Response({'error': 'Invalid time format. Use HH:MM format.'}, status=status.HTTP_400_BAD_REQUEST)

        pharmacies = Pharmacy.objects.all()
        open_pharmacies = []

        # 正則表示式match開放時間範圍
        time_pattern = re.compile(
            r'(?P<days>[A-Za-z, -]+) (?P<start_time>\d{2}:\d{2}) - (?P<end_time>\d{2}:\d{2})'
        )

        for pharmacy in pharmacies:
            # 藥局的開放時間
            opening_hours_periods = pharmacy.opening_hours.split(' / ')

            for period in opening_hours_periods:
                match = time_pattern.match(period)
                if match:
                    days_range = match.group('days').strip()
                    start_time = datetime.strptime(match.group('start_time'), '%H:%M').time()
                    end_time = datetime.strptime(match.group('end_time'), '%H:%M').time()

                    # 處理日期範圍
                    days = self.parse_days(days_range)
                    if weekday in days:
                        # 檢查時間範圍
                        if start_time <= end_time:  # 不跨日
                            if start_time <= query_time <= end_time:
                                open_pharmacies.append({'name': pharmacy.name})
                                break
                        else:  # 跨日
                            if query_time >= start_time or query_time <= end_time:
                                open_pharmacies.append({'name': pharmacy.name})
                                break

        return Response(open_pharmacies, status=status.HTTP_200_OK)

    def parse_days(self, days_range):
        """
        處理日期範圍字符串，例如 "Fri - Sun" 或 "Mon, Tue"
        """
        days_map = {'Mon': 'Mon', 'Tue': 'Tue', 'Wed': 'Wed', 'Thu': 'Thu', 'Fri': 'Fri', 'Sat': 'Sat', 'Sun': 'Sun'}
        days = set()

        # 處理 "Mon, Tue" 格式
        if ',' in days_range:
            for day in days_range.split(', '):
                if day in days_map:
                    days.add(day)
        else:
            # 處理 "Fri - Sun" 格式
            parts = days_range.split(' - ')
            if len(parts) == 2:
                start_day, end_day = parts
                days_list = list(days_map.keys())
                try:
                    start_index = days_list.index(start_day)
                    end_index = days_list.index(end_day)
                    if start_index <= end_index:
                        days.update(days_list[start_index:end_index + 1])
                except ValueError:
                    pass  #不處理其他日期格式 僅限 Mon, Tue ,.....

        return days #回傳{'Mon', 'Wed', 'Fri',....}

