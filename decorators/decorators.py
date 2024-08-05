from functools import wraps
from django.http import HttpResponseForbidden

def role_required(roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_roles = request.user.roles.values_list('name', flat=True)
            if not any(role in user_roles for role in roles):
                return HttpResponseForbidden("You do not have permission to access this resource.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
