from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def teacher_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_active or not user.is_teacher():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return login_required(wrapped)