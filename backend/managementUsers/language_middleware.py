from django.utils.translation import activate

from backend.managementUsers.models import Profile
from backend.settings.models import System

class SetLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            user_language = Profile.objects.get(id=request.user.id).language
        except Profile.DoesNotExist: # If there is no user connected, language will be taked from settings
            user_language = System.objects.get().language
        except Exception:  # English is the default language
            user_language = "en"

        activate(user_language)

        response = self.get_response(request)

        return response
