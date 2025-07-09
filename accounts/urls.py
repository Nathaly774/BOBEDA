from django.urls import path
from accounts.views import SignupView, LoginView  # Asegúrate de importar desde 'accounts'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
]