'''
UserSerializer: Valida y crea usuarios

CustomTokenObtainPairSerializer: Personaliza el token JWT

BookSerializer y AuthorSerializer: Convierten modelos a JSON
'''

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Author, Genre, Rating
#from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

'''  
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

'''

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Muestra el nombre del usuario

    class Meta:
        model = Rating
        fields = ['id', 'user', 'book', 'score', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']  # Campos autogenerados

class BookSerializer(serializers.ModelSerializer):
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True) #nuevo
    genres = GenreSerializer(many=True, read_only=True)  # Solo lectura en la respuesta
    genre_ids = serializers.PrimaryKeyRelatedField(  # Para enviar IDs al crear/actualizar
        queryset=Genre.objects.all(),
        source='genres',
        many=True,
        write_only=True,
        required=False
    )
    ratings = RatingSerializer(many=True, read_only=True, source='rating_set')  # Muestra todas las calificaciones
    average_rating = serializers.SerializerMethodField()  # Calcula el promedio

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'ratings', 'average_rating', ...]  # Añade los campos que ya tenías

    def get_average_rating(self, obj):
        ratings = obj.rating_set.all()
        if ratings:
            return sum(r.score for r in ratings) / len(ratings)
        return 0
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'published_date', 'isbn', 'stock', 'ratings', 'average_rating', 'download_url', 'genres', 'genre_ids',]

