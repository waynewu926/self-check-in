from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Customer

# 注册功能
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        phone = data.get('phone')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            return JsonResponse({'message': 'Passwords do not match'}, status=400)

        if Customer.objects.filter(phone=phone).exists():
            return JsonResponse({'message': 'Phone number already registered'}, status=400)

        customer = Customer.objects.create(name=name, phone=phone, password=password)
        return JsonResponse({'message': 'Registration successful', 'id': customer.id}, status=201)

    return JsonResponse({'message': 'Invalid request method'}, status=405)

# 登录功能
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone')
        password = data.get('password')

        customer = Customer.objects.filter(phone=phone, password=password).first()
        if customer:
            return JsonResponse({'message': 'Login successful', 'id': customer.id}, status=200)

        return JsonResponse({'message': 'Invalid phone number or password'}, status=400)

    return JsonResponse({'message': 'Invalid request method'}, status=405)
