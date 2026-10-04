# Importe les fonctions permettant de définir les URLs de notre application.
from django.urls import path

# Importe les deux vues API utilisées pour gérer la liste et le détail des produits.
from .views import ProductListAPIView, ProductDetailAPIView


# Définit les routes disponibles pour les produits dans l'API.
urlpatterns = [
    # Retourne la liste de tous les produits et permet d'en créer un nouveau.
    path("products/", ProductListAPIView.as_view(), name="product-list"),

    # Retourne les informations d'un seul produit grâce à son identifiant.
    path("products/<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),
]