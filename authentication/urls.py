from django.urls import path,include
from .views import *


urlpatterns = [
    path('hello', hello_world, name='hello'),
    path('logout', logout_view, name='logout'),
    # path('login-success', login_success_view, name='login_success'),
    path('accounts/', include('allauth.urls')), 
    path('api/user/projects/', user_projects_view, name='user_projects'),
    path('google-auth/', google_auth_redirect, name='google-auth-redirect'),
    path('oauth2/callback/', google_auth_callback, name='google-auth-callback'),
    path('save-paper/', save_research_paper, name='save_research_paper'),
    path('get-papers/', extract_information, name='get_research_papers'),
    path('url_headers/', url_headers, name='url_headers'),
]