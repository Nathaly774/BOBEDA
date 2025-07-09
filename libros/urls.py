from django.urls import path
from libros.views import BookListCreateView, BookDetailView, RatingCreateView, RatingListView, BookRecommendationView, LibrosAnalisisView,LibrosPorGeneroView

urlpatterns = [
    path('', BookListCreateView.as_view(), name='book-list'),
    path('<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('<int:book_id>/ratings/', RatingListView.as_view(), name='rating-list'),
    path('ratings/create/', RatingCreateView.as_view(), name='rating-create'),
    path('recommend/', BookRecommendationView.as_view(), name='book-recommend'),
    path('analisis/', LibrosAnalisisView.as_view(), name='libros-analisis'),
    path('recomendaciones/', LibrosPorGeneroView.as_view(), name='libros-por-genero'),
]