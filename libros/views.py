from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Avg
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from .models import Rating, Book, Genre, Author
from .serializers import RatingSerializer
from django_filters.rest_framework import DjangoFilterBackend  #django-filter
from .serializers import BookSerializer, AuthorSerializer

import os
import matplotlib.pyplot as plt
from django.http import FileResponse  # Muestra el

'''
#Vista de Registro (Signup)
class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Vista de Login (Token generación):
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

'''
#Vistas CRUD para Libros


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['genres']  # Filtra por genres=1


class RatingCreateView(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]  # Solo usuarios autenticados

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Asigna automáticamente el usuario logueado

class RatingListView(generics.ListAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        book_id = self.kwargs['book_id']
        return Rating.objects.filter(book_id=book_id)
    
class BookRecommendationView(APIView):
    def get(self, request):
        # Parámetros del usuario (ej: /api/books/recommend/?genres=1,2&min_rating=4)
        genre_ids = request.GET.get('genres', '').split(',')  # Ej: '1,2' → [1, 2]
        min_rating = float(request.GET.get('min_rating', 0))  # Valoración mínima

        # Filtra libros que tengan AL MENOS UNO de los géneros solicitados
        books = Book.objects.filter(
            genres__id__in=genre_ids
        ).annotate(
            avg_rating=Avg('rating__score')  # Anotación para el promedio
        ).filter(
            avg_rating__gte=min_rating  # Filtra por valoración mínima
        ).order_by(
            '-avg_rating'  # Ordena de mejor a peor valoración
        ).distinct()  # Evita duplicados

        # Serializa los resultados
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
class LibrosAnalisisView(APIView):
    def get(self, request):
        libros = Book.objects.annotate(
            avg_rating=Avg('rating__score')
        ).values('id', 'title', 'genres', 'avg_rating')
        return Response(list(libros))
    
class LibrosPorGeneroView(APIView):
    def get(self, request):
        genre_id = request.GET.get('genre_id')
        min_rating = float(request.GET.get('min_rating', 0))
        
        libros = Book.objects.filter(
            genres__id=genre_id
        ).annotate(
            avg_rating=Avg('rating__score')
        ).filter(
            avg_rating__gte=min_rating
        ).order_by('-avg_rating')
        
        serializer = BookSerializer(libros, many=True)
        return Response(serializer.data)