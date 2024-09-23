from functools import wraps
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated

def has_functionality(required_functionalities):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({'detail': 'Authentication required.'}, status=401)

            # Get the user's role and functionalities
            # user_roles = request.user.role.all() 
            user_roles = request.user
            print({"user_roles":user_roles})
            user_functionalities = set()

            for role in user_roles:
                user_functionalities.update(role.functionalities)  # Assuming functionalities is a list or set

            # Check if user has any of the required functionalities or has 'all'
            if 'all' in user_functionalities or any(func in user_functionalities for func in required_functionalities):
                return view_func(request, *args, **kwargs)

            return JsonResponse({'detail': 'Permission denied.'}, status=403)

        return _wrapped_view
    return decorator
