from django.contrib import admin
from .models import Author  # Importa el modelo Author
from .models import Book
from .models import Genre
from .models import Rating

admin.site.register(Book)
admin.site.register(Author)  # Registra el modelo en el admin
admin.site.register(Genre)
admin.site.register(Rating)
