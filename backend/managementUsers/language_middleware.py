from django.utils.translation import activate
from django.conf import settings

from backend.managementUsers.models import Profile

class SetLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            user_language = Profile.objects.get(id=request.user.id).language
            print(user_language)
        except Profile.DoesNotExist:
            user_language = 'en'

        activate(user_language)

        response = self.get_response(request)

        return response
