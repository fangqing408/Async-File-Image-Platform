import logging
import traceback
from django.http import JsonResponse


logger = logging.getLogger(__name__)


def handle_exception(request, exception, default_message='服务器内部错误'):
    logger.error(f'Request failed: {request.path}')
    logger.error(f'Exception: {exception}')
    logger.error(f'Traceback: {traceback.format_exc()}')

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'status': 'error',
            'message': str(exception) if hasattr(exception, 'args') else default_message
        }, status=500)

    return None


def validate_email(email):
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def validate_phone(phone):
    if not phone:
        return True
    import re
    phone_pattern = r'^1[3-9]\d{9}$|^0\d{2,3}-\d{7,8}$'
    return re.match(phone_pattern, phone) is not None


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_random_string(length=16):
    import random
    import string
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))