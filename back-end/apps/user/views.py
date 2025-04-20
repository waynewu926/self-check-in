from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, RegisterSerializer
from .models import User

class RegisterView(APIView):
    # 移除权限验证
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # 简单创建token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    # 移除权限验证
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        
        try:
            # 根据手机号查找用户
            user = User.objects.get(phone=phone)
            # 简单验证密码
            if user.check_password(password):
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "user": UserSerializer(user).data,
                    "token": token.key
                })
            else:
                return Response({"error": "密码错误"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    # 简化用户详情获取
    def get(self, request):
        # 简单返回用户信息，不做权限验证
        token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1] if 'HTTP_AUTHORIZATION' in request.META else None
        
        if token:
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
                return Response(UserSerializer(user).data)
            except Token.DoesNotExist:
                pass
        
        return Response({"error": "未登录"}, status=status.HTTP_401_UNAUTHORIZED)
