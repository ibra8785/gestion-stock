# Importe les outils de Django REST Framework et le modèle Product que notre API devra exposer.
from rest_framework import serializers

from .models import Product

# Définit le serializer du produit afin de convertir les données du modèle Product en données utilisables par notre API.
class ProductSerializer(serializers.ModelSerializer):
    # Configure le serializer pour utiliser le modèle Product et tous ses champs.
    class Meta:
        model = Product
        fields = "__all__"