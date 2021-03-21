from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *


urlpatterns = [
   path('login/', LoginView.as_view()),
   path('logout/', LogoutView.as_view()),
   path('program_launcher/', ReturnLauncherView.as_view()),
   path('get_program/', ReturnProgramView.as_view()),
   path('check_version_launcher/', CheckVersionLauncherView.as_view()),
   path('check_version_programs/', CheckVersionProgramView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)