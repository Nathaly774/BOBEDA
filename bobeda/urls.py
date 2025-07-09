'''
POST /api/signup/: Registro de usuarios.

POST /api/login/: Genera token JWT.

GET/POST /api/books/: Lista o crea libros.

GET/PUT/DELETE /api/books/<id>/: Operaciones por libro.
'''

from django.contrib import admin
from django.urls import path, include  # Añade 'include' para modularizar rutas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),  # Autenticación (signup, login)
    path('api/books/', include('libros.urls')),   # Todo lo de libros y ratings
]