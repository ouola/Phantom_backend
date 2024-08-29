from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Pharmacy, Mask
import re
from datetime import datetime



class PharmacyByOpeningHoursAPIView(APIView):
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

class MasksByPharmacyAPIView(APIView):

    def get(self, request, *args, **kwargs):
        pharmacy_name = request.query_params.get('pharmacy_name')
        sort_by = request.query_params.get('sort_by', 'name')  # 默認按名稱排序

        if not pharmacy_name:
            return Response({'error': 'Pharmacy name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 確保輸入是 name 或者是 price
        if sort_by not in ['name', 'price']:
            return Response({'error': 'Invalid sort_by parameter. Use "name" or "price".'}, status=status.HTTP_400_BAD_REQUEST)

        # 找尋藥局名稱
        pharmacy = Pharmacy.objects.filter(name=pharmacy_name).first()
        
        if not pharmacy:
            return Response({'error': 'Pharmacy not found.'}, status=status.HTTP_404_NOT_FOUND)

        # 查詢該藥局的口罩並按name或是price排序
        masks = Mask.objects.filter(pharmacy=pharmacy).order_by(sort_by)

        # 組織回應數據
        mask_list = [
            {
                'name': mask.name,
                'price': str(mask.price), 
            }
            for mask in masks
        ]

        return Response(mask_list, status=status.HTTP_200_OK)
    
class PharmaciesByMaskCountAPIView(APIView):
    def get(self, request):
        comparison = request.query_params.get('comparison')  # 'more' or 'less'
        count = request.query_params.get('count')
        min_price = request.query_params.get('min_price', 0)  # 默認為 0
        max_price = request.query_params.get('max_price') # require

        if not count or not comparison or not max_price:
            return Response({'error': 'Comparison, count, and max_price parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if comparison not in ['more', 'less']:
            return Response({'error': 'Comparison must be either "more" or "less".'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            count = int(count)
            min_price = float(min_price)
            max_price = float(max_price)
        except ValueError:
            return Response({'error': 'Count must be an integer, and min_price and max_price must be floats.'}, status=status.HTTP_400_BAD_REQUEST)

        pharmacies = Pharmacy.objects.all()
        matching_pharmacies = []

        for pharmacy in pharmacies:
            mask_count = pharmacy.masks.filter(price__gte=min_price, price__lte=max_price).count()
            if (comparison == 'more' and mask_count >= count) or (comparison == 'less' and mask_count <= count):
                matching_pharmacies.append({'name': pharmacy.name, 'mask_count': mask_count})

        return Response(matching_pharmacies, status=status.HTTP_200_OK)