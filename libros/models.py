'''
blank=True: Permite que el campo esté vacío en formularios

null=True: Permite NULL en la base de datos

unique=False: Elimina la restricción de unicidad (si no la necesitas)

verbose_name y help_text: Mejoran la experiencia en el panel admin.
'''
from django.db import models
from django.contrib.auth.models import User  # Importa el modelo User de Django
from django.db.models import Avg # Calcular promedio

class Author(models.Model):
    name = models.CharField(max_length=100)
    #email = models.EmailField(unique=True)
    email = models.EmailField(blank=True, null=True, unique=False)  #opcional
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del género")
    
    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    stock = models.PositiveIntegerField(default=0)
    download_url = models.URLField(
        blank=True,  # No es obligatorio llenarlo
        null=True,   # Permite valores NULL en la base de datos
        verbose_name="Enlace de descarga",
        help_text="URL para descargar el libro (ej: https://ejemplo.com/libro.pdf)"  # Texto de ayuda
    )
    genres = models.ManyToManyField(
        Genre, 
        blank=True,  #El libro puede no tener géneros
        verbose_name="Géneros",
        help_text="Selecciona uno o varios géneros para este libro"
    )
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Ranking promedio" # Calcula el promedio 
    )
    
    def update_average_rating(self):
        """Actualiza el promedio de calificaciones cada vez que se modifica una reseña."""
        avg_rating = self.rating_set.aggregate(Avg('score'))['score__avg'] or 0
        self.average_rating = round(avg_rating, 2)
        self.save()

    def __str__(self):
        return self.title
    

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Libro")
    score = models.PositiveSmallIntegerField(
        choices=[(1, '1 ⭐'), (2, '2 ⭐⭐'), (3, '3 ⭐⭐⭐'), (4, '4 ⭐⭐⭐⭐'), (5, '5 ⭐⭐⭐⭐⭐')],
        verbose_name="Puntuación"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Comentario")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        unique_together = ('user', 'book')  # Evita que un usuario califique el mismo libro múltiples veces

    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guarda la calificación
        self.book.update_average_rating()  # Actualiza el promedio del libro

    def delete(self, *args, **kwargs):
        book = self.book
        super().delete(*args, **kwargs)  # Elimina la calificación
        book.update_average_rating()  # Actualiza el promedio del libro
        
    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.score}⭐"