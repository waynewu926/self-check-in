from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, timedelta
import json
from .models import Room, Booking

def validate_dates(check_in_date, check_out_date, date_format='%Y-%m-%d'):
    """验证日期格式和逻辑"""
    try:
        # 验证日期格式
        check_in_date_obj = datetime.strptime(check_in_date, date_format).date()
        check_out_date_obj = datetime.strptime(check_out_date, date_format).date()
        
        # 验证日期逻辑
        if check_in_date_obj >= check_out_date_obj:
            return False, '退房日期必须晚于入住日期'
        
        return True, (check_in_date_obj, check_out_date_obj)
    
    except (ValueError, TypeError):
        return False, '日期格式不正确'

def available_rooms(request):
    """获取可用房间列表"""
    try:
        # 获取查询参数
        check_in_date = request.GET.get('check_in_date')
        check_out_date = request.GET.get('check_out_date')
        room_type = request.GET.get('room_type')
        
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # 验证日期
        is_valid, result = validate_dates(check_in_date, check_out_date)
        if not is_valid:
            return JsonResponse({'error': result}, status=400)
        
        check_in_date, check_out_date = result
        
        # 构建查询条件
        query = Q()
        if room_type is not None and room_type != '':
            query &= Q(room_detail__room_type=int(room_type))
        
        # 获取所有符合条件的房间
        rooms = Room.objects.filter(query)
        
        # 筛选出可用的房间
        available_rooms = []
        for room in rooms:
            if Booking.is_room_available(room.id, check_in_date, check_out_date):
                room_data = {
                    'id': room.id,
                    'room_number': room.room_number,
                    'room_type': room.room_detail.get_room_type_display(),
                    'price': room.room_detail.price,
                }
                available_rooms.append(room_data)
        
        # 计算总记录数
        total = len(available_rooms)
        
        # 分页处理
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_rooms = available_rooms[start_index:end_index]
        
        return JsonResponse({
            'rooms': paginated_rooms,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def room_detail(request, room_id):
    """获取房间详情"""
    try:
        room = get_object_or_404(Room, id=room_id)
        room_data = {
            'id': room.id,
            'room_number': room.room_number,
            'room_type': room.room_detail.get_room_type_display(),
            'price': room.room_detail.price,
        }
        return JsonResponse(room_data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def create_booking(request):
    """创建预订"""
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # 获取必要参数
        room_id = data.get('room_id')
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        guest_name = data.get('guest_name')
        guest_phone = data.get('guest_phone')
        guest_id_card = data.get('guest_id_card')
        guest_count = data.get('guest_count', 1)
        
        # 验证参数
        if not all([room_id, check_in_date, check_out_date, guest_name, guest_phone, guest_id_card]):
            return JsonResponse({'error': '缺少必要参数'}, status=400)
        
        # 验证日期
        is_valid, result = validate_dates(check_in_date, check_out_date)
        if not is_valid:
            return JsonResponse({'error': result}, status=400)
        
        check_in_date, check_out_date = result
        
        # 验证房间是否可用
        room = get_object_or_404(Room, id=room_id)
        if not Booking.is_room_available(room_id, check_in_date, check_out_date):
            return JsonResponse({'error': '该房间在所选日期不可用'}, status=400)
        
        # 创建预订记录
        booking = Booking(
            customer=request.user,
            room=room,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            booking_status=1,  # 待入住
            guest_name=guest_name,
            guest_phone=guest_phone,
            guest_id_card=guest_id_card,
            guest_count=guest_count
        )

        # 先保存对象，获取主键
        booking.save()

        # 然后生成各种字段
        booking_number = booking.generate_booking_number()
        code = booking.generate_code()
        room_password = booking.generate_room_password()
        
        # 返回预订信息
        return JsonResponse({
            'booking_id': booking.id,
            'booking_number': booking.booking_number,
            'room_number': room.room_number,
            'room_type': room.room_detail.get_room_type_display(),
            'check_in_date': check_in_date.strftime('%Y-%m-%d'),
            'check_out_date': check_out_date.strftime('%Y-%m-%d'),
            'total_price': booking.total_price,
            'code': code,
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def booking_list(request):
    """获取用户的预订列表"""
    try:
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # 获取筛选参数
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status = request.GET.get('status')
        
        # 构建查询条件
        query = Q(customer=request.user)
        
        if status is not None and status != '':
            query &= Q(booking_status=int(status))
            
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                # 查找日期范围内有重叠的预订
                query &= Q(check_in_date__lte=end_date, check_out_date__gte=start_date)
            except ValueError:
                pass
        
        # 获取总记录数
        total_bookings = Booking.objects.filter(query).count()
        
        # 获取分页数据
        bookings = Booking.objects.filter(query).order_by('-check_in_date')[(page-1)*page_size:page*page_size]
        
        booking_list = []
        for booking in bookings:
            booking_data = {
                'id': booking.id,
                'booking_number': booking.booking_number,
                'room_number': booking.room.room_number,
                'room_type': booking.room.room_detail.room_type,
                'room_type_name': booking.room.room_detail.get_room_type_display(),
                'check_in_date': booking.check_in_date.strftime('%Y-%m-%d'),
                'check_out_date': booking.check_out_date.strftime('%Y-%m-%d'),
                'total_price': booking.total_price,
                'booking_status': booking.booking_status,
                'booking_status_name': booking.get_booking_status_display(),
                'guest_name': booking.guest_name,
                'guest_phone': booking.guest_phone,
                'guest_id_card': booking.guest_id_card,
                'guest_count': booking.guest_count,
                'code': booking.code,
                'comment': booking.comment,
                'comment_time': booking.comment_time.strftime('%Y-%m-%d %H:%M:%S') if booking.comment_time else None,
            }
            booking_list.append(booking_data)
        
        return JsonResponse({
            'bookings': booking_list,
            'total': total_bookings,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_bookings + page_size - 1) // page_size
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def update_booking_status(request, booking_id):
    """更新预订状态"""
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        status = data.get('status')
        
        if status is None:
            return JsonResponse({'error': '缺少状态参数'}, status=400)
        
        booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
        booking.booking_status = status
        booking.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def add_comment(request, booking_id):
    """添加评价"""
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        comment = data.get('comment')
        
        if not comment:
            return JsonResponse({'error': '评价内容不能为空'}, status=400)
        
        booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
        
        # 验证预订状态是否为"已完成"
        if booking.booking_status != 3:
            return JsonResponse({'error': '只有已完成的预订才能评价'}, status=400)
        
        # 添加评价
        booking.comment = comment
        booking.comment_time = datetime.now()
        booking.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def verify_check_in_code(request):
    """验证入住验证码"""
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        code = data.get('code')
        update_status = data.get('update_status', True)  # 默认为True，保持向后兼容
        
        if not code:
            return JsonResponse({'error': '验证码不能为空'}, status=400)
        
        # 查找匹配的预订记录 - 修改：不再限制只查找待入住状态的记录
        booking = Booking.objects.filter(
            code=code,
            booking_status__in=[1, 2]  # 1=待入住, 2=已入住
        ).first()
        
        if not booking:
            return JsonResponse({'error': '验证码无效或已过期'}, status=400)
        
        # 只有当update_status为True且状态为待入住时才更新状态
        if update_status and booking.booking_status == 1:
            booking.booking_status = 2  # 已入住
            booking.save()
        
        # 计算密码有效期（退房日期）
        password_expiry = booking.check_out_date.strftime('%Y-%m-%d')
        
        # 返回完整的预订信息，包括预订状态
        return JsonResponse({
            'success': True,
            'booking_status': booking.booking_status,  # 添加预订状态
            'room_number': booking.room.room_number,
            'room_password': booking.room_password,
            'password_expiry': password_expiry,
            'guest_name': booking.guest_name,
            'guest_phone': booking.guest_phone,
            'guest_id_card': booking.guest_id_card,
            'guest_count': booking.guest_count,
            'room_type': booking.room.room_detail.room_type,
            'check_in_date': booking.check_in_date.strftime('%Y-%m-%d'),
            'booking_number': booking.booking_number,
            'tips': '如需任何帮助，请拨打前台电话：8888'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def confirm_check_in(request):
    """确认入住，更新预订状态"""
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({'error': '验证码不能为空'}, status=400)
        
        # 查找匹配的预订记录
        booking = Booking.objects.filter(
            code=code,
            booking_status=1  # 待入住状态
        ).first()
        
        if not booking:
            return JsonResponse({'error': '验证码无效或已过期'}, status=400)
        
        # 更新预订状态为已入住
        booking.booking_status = 2  # 已入住
        booking.save()
        
        return JsonResponse({
            'success': True,
            'message': '确认入住成功'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def check_out(request):
    """处理退房请求"""
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({'error': '验证码不能为空'}, status=400)
        
        # 查找匹配的预订记录
        booking = Booking.objects.filter(
            code=code,
            booking_status=2  # 已入住状态
        ).first()
        
        if not booking:
            return JsonResponse({'error': '验证码无效或房间未处于入住状态'}, status=400)
        
        # 更新预订状态为已完成
        booking.booking_status = 3  # 已完成
        booking.save()
        
        return JsonResponse({
            'success': True,
            'message': '退房成功，感谢您的入住！'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
