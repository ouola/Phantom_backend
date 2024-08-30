from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Pharmacy, Mask, User, PurchaseHistory
import re
from datetime import datetime
from django.db.models import Sum


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
    
class TopUsersByTransactionAPIView(APIView):
    def get(self, request):
        top_x = request.query_params.get('top_x')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not top_x or not start_date or not end_date:
            return Response({'error': 'top_x, start_date, and end_date parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 確保 top_x 是否為整數
        try:
            top_x = int(top_x)
        except ValueError:
            return Response({'error': 'top_x must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        # 確保日期格式
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'start_date and end_date must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

        # 確保 end_date 不早於 start_date
        if end_date < start_date:
            return Response({'error': 'end_date cannot be before start_date.'}, status=status.HTTP_400_BAD_REQUEST)

        # 查詢 top_x 用戶，按交易總金額 大->小
        top_users = User.objects.filter(
            purchases__transaction_date__range=[start_date, end_date]
        ).annotate(total_amount=Sum('purchases__transaction_amount')).order_by('-total_amount')[:top_x]

        user_data = [
            {
            'name': user.name,
            'total_amount': user.total_amount
            }
            for user in top_users
        ]

        return Response(user_data, status=status.HTTP_200_OK)
    
    from rest_framework.views import APIView


class TotalMasksAndTransactionValueAPIView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({'error': 'start_date and end_date parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 確保日期格式正確
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        if start_date > end_date:
            return Response({'error': 'Start date must be before or equal to end date.'}, status=status.HTTP_400_BAD_REQUEST)

        # 計算總面罩數量和交易總額
        total_masks = PurchaseHistory.objects.filter(
            transaction_date__range=[start_date, end_date]
        ).count()  # 總面罩數量（記錄數量）

        total_amount = PurchaseHistory.objects.filter(
            transaction_date__range=[start_date, end_date]
        ).aggregate(total_amount=Sum('transaction_amount'))['total_amount']  # 總交易金額

        if total_amount is None:
            total_amount = 0  # 如果沒有記錄，設置為 0

        return Response({
            'total_masks': total_masks,
            'total_amount': total_amount
        }, status=status.HTTP_200_OK)
