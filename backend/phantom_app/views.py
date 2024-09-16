from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Pharmacy, Mask, User, PurchaseHistory, OpeningHour
import re
from datetime import datetime
from django.db.models import Sum, Case, When, IntegerField
from django.utils import timezone
from django.db import transaction

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

        open_pharmacies = []

        # 查詢開放時間符合要求的藥局
        pharmacies = Pharmacy.objects.all()

        for pharmacy in pharmacies:
            # 查找所有符合要求的開放時間紀錄
            opening_hours = OpeningHour.objects.filter(pharmacy=pharmacy, day_of_week=weekday)

            for opening_hour in opening_hours:
                if self.is_time_within_range(query_time, opening_hour.start_time, opening_hour.end_time):
                    open_pharmacies.append({'name': pharmacy.name})
                    break

        return Response(open_pharmacies, status=status.HTTP_200_OK)

    def is_time_within_range(self, query_time, start_time, end_time):
        # 檢查時間範圍
        if start_time <= end_time:  # 不跨日
            return start_time <= query_time <= end_time
        else:  # 跨日
            return query_time >= start_time or query_time <= end_time

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

        # 驗證必要參數
        if not top_x or not start_date or not end_date:
            return Response({'error': 'top_x, start_date, and end_date parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 確保 top_x 為整數
        try:
            top_x = int(top_x)
        except ValueError:
            return Response({'error': 'top_x must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        # 驗證日期格式
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'start_date and end_date must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

        # 確保 end_date 不早於 start_date
        if end_date < start_date:
            return Response({'error': 'end_date cannot be before start_date.'}, status=status.HTTP_400_BAD_REQUEST)

        # 查詢 top_x 用戶，按交易總金額排序
        top_users = User.objects.filter(
            purchase_histories__transaction_date__range=[start_date, end_date]
        ).annotate(total_amount=Sum('purchase_histories__transaction_amount')).order_by('-total_amount')[:top_x]

        # 構建返回資料
        user_data = [
            {
                'name': user.name,
                'total_amount': user.total_amount
            }
            for user in top_users
        ]

        return Response(user_data, status=status.HTTP_200_OK)

    

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

class SearchAPIView(APIView):
    def get(self, request):
        search_term = request.query_params.get('search_term', '')

        if not search_term:
            return Response({'error': 'search_term parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 查詢藥局和口罩，並按關聯性排序
        pharmacies = Pharmacy.objects.filter(name__icontains=search_term).annotate(
            relevance=Case(
                When(name__istartswith=search_term, then=2),
                When(name__iexact=search_term, then=1),
                default=0,
                output_field=IntegerField(),
            )
        ).order_by('-relevance', 'name')

        masks = Mask.objects.filter(name__icontains=search_term).annotate(
            relevance=Case(
                When(name__istartswith=search_term, then=2),
                When(name__iexact=search_term, then=1),
                default=0,
                output_field=IntegerField(),
            )
        ).order_by('-relevance', 'name')

        results = {
            'pharmacies': [{'id': pharmacy.id, 'name': pharmacy.name} for pharmacy in pharmacies] if pharmacies.exists() else None,
            'masks': [{'id': mask.id, 'name': mask.name, 'pharmacy': mask.pharmacy.name} for mask in masks] if masks.exists() else None
        }

        return Response(results, status=status.HTTP_200_OK)

class PurchaseMaskAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_name = request.data.get('user_name')
        pharmacy_name = request.data.get('pharmacy_name')
        mask_name = request.data.get('mask_name')
        quantity = request.data.get('quantity', 0)  # 默認0個

        # 驗證 quantity 是否為正整數
        if not isinstance(quantity, int) or quantity <= 0:
            return Response({"error": "Quantity must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 根據名稱找用戶、藥局和口罩
            user = User.objects.get(name=user_name)
            pharmacy = Pharmacy.objects.get(name=pharmacy_name)
            mask = Mask.objects.get(pharmacy=pharmacy, name=mask_name)

            total_price = mask.price * quantity

            if user.cash_balance < total_price:
                return Response({"error": "Insufficient user balance"}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                # 更新用戶餘額
                user.cash_balance -= total_price
                user.save()

                # 更新藥局現金餘額
                pharmacy.cash_balance += total_price
                pharmacy.save()

                # 更新購買歷史
                purchase_history = PurchaseHistory.objects.create(
                    user=user,
                    pharmacy_name=pharmacy.name,
                    mask_name=mask.name,
                    transaction_amount=total_price,
                    transaction_date=timezone.now().date(),  # 只取日期部分
                    transaction_time=timezone.now().time(),  # 只取時間部分
                )

            return Response({
                "message": "Purchase successful",
                "purchase_details": {
                    "user": user.name,
                    "pharmacy": pharmacy.name,
                    "mask": mask.name,
                    "quantity": quantity,
                    "total_price": total_price
                }
            }, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Pharmacy.DoesNotExist:
            return Response({"error": "Pharmacy does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Mask.DoesNotExist:
            return Response({"error": "Mask does not exist in the specified pharmacy"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)