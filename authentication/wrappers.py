from functools import wraps
from .validate import introspect_token
from django.http import JsonResponse

def oauth_token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('token')

        if not token:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        if not introspect_token(token):
            return JsonResponse({'error': 'Un validated'}, status=401)

        # Token is valid, proceed to the decorated view
        return view_func(request, *args, **kwargs)

    return wrapper
