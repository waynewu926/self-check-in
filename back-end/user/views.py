from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
import json

# 注册功能
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        phone = data.get('phone')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # 验证手机号长度
        if not phone or len(phone) != 11:
            return JsonResponse({'message': '手机号必须是11位'}, status=400)
            
        # 验证手机号格式
        if not phone.isdigit():
            return JsonResponse({'message': '手机号必须全部是数字'}, status=400)

        if password != confirm_password:
            return JsonResponse({'message': '密码不匹配'}, status=400)

        if User.objects.filter(username=phone).exists():
            return JsonResponse({'message': '手机号已注册'}, status=400)

        # 创建User模型实例
        user = User.objects.create_user(
            username=phone,  # 使用手机号作为用户名
            password=password,  # create_user会自动哈希处理密码
            first_name=name
        )
        
        return JsonResponse({'message': '注册成功', 'id': user.id}, status=201)

    return JsonResponse({'message': '无效的请求方法'}, status=405)

# 登录功能
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone')
        password = data.get('password')

        # 使用Django的认证系统
        user = authenticate(username=phone, password=password)
        if user is not None:
            auth_login(request, user)  # 创建会话
            
            return JsonResponse({
                'message': '登录成功', 
                'id': user.id,
                'name': user.first_name,
                'phone': user.username,
                'session_id': request.session.session_key
            }, status=200)
        else:
            return JsonResponse({'message': '手机号或密码无效'}, status=400)

    return JsonResponse({'message': '无效的请求方法'}, status=405)

# 获取用户信息
@login_required
def user_info(request):
    if request.method == 'GET':
        # 获取当前登录用户
        user = request.user
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': user.id,
                'name': user.first_name,
                'phone': user.username
            }
        })
    
    return JsonResponse({'message': '无效的请求方法'}, status=405)
