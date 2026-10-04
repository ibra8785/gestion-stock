# Importe l'outil Django qui retourne automatiquement une réponse 404 si l'objet demandé n'existe pas.
from django.shortcuts import get_object_or_404

# Importe les outils nécessaires pour créer une vue API et envoyer une réponse HTTP.
from rest_framework.views import APIView
from rest_framework.response import Response

# Importe notre modèle Product et le serializer qui transforme les produits en données API.
from .models import Product
from .serializers import ProductSerializer


# Crée la vue API qui permet de récupérer la liste des produits et d'en créer un nouveau.
class ProductListAPIView(APIView):

    # Traite les requêtes GET envoyées à cette vue.
    def get(self, request):

        # Récupère tous les produits enregistrés dans la base de données.
        products = Product.objects.all()

        # Transforme la liste des produits en données que l'API peut retourner.
        serializer = ProductSerializer(products, many=True)

        # Renvoie les produits au client dans une réponse HTTP.
        return Response(serializer.data)

    # Traite les requêtes POST envoyées pour créer un nouveau produit.
    def post(self, request):

        # Récupère et valide les données envoyées par le client grâce au serializer.
        serializer = ProductSerializer(data=request.data)

        # Vérifie que les données respectent les règles du modèle Product.
        if serializer.is_valid():

            # Enregistre le nouveau produit dans la base de données.
            serializer.save()

            # Retourne le produit nouvellement créé avec le statut HTTP 201.
            return Response(serializer.data, status=201)

        # Retourne les erreurs de validation si les données sont incorrectes.
        return Response(serializer.errors, status=400)


# Crée la vue API qui permet de consulter un seul produit à partir de son identifiant.
class ProductDetailAPIView(APIView):

    # Traite les requêtes GET envoyées pour récupérer un produit précis.
    def get(self, request, pk):

        # Récupère le produit demandé ou retourne automatiquement une réponse HTTP 404 s'il n'existe pas.
        product = get_object_or_404(Product, pk=pk)

        # Transforme le produit Django en données que l'API peut retourner.
        serializer = ProductSerializer(product)

        # Renvoie les informations du produit au format JSON.
        return Response(serializer.data)

    # Traite les requêtes PUT envoyées pour modifier complètement un produit.
    def put(self, request, pk):

        # Récupère le produit demandé ou retourne automatiquement une réponse HTTP 404 s'il n'existe pas.
        product = get_object_or_404(Product, pk=pk)

        # Charge les nouvelles données dans le serializer en les comparant au produit existant.
        serializer = ProductSerializer(product, data=request.data)

        # Vérifie que toutes les données envoyées respectent les règles du produit.
        if serializer.is_valid():

            # Enregistre les modifications dans la base de données.
            serializer.save()

            # Retourne le produit modifié avec un statut HTTP 200.
            return Response(serializer.data)

        # Retourne les erreurs si les données envoyées sont incorrectes.
        return Response(serializer.errors, status=400)

    # Traite les requêtes DELETE envoyées pour supprimer un produit.
    def delete(self, request, pk):

        # Récupère le produit demandé ou retourne automatiquement une réponse 404 s'il n'existe pas.
        product = get_object_or_404(Product, pk=pk)

        # Supprime définitivement le produit de la base de données.
        product.delete()

        # Confirme que la suppression a été effectuée avec le statut HTTP 204.
        return Response(status=204)