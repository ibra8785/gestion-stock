# Importe l'outil Django qui retourne automatiquement une réponse 404 si l'objet demandé n'existe pas.
from django.shortcuts import get_object_or_404

# Importe les outils nécessaires pour créer une vue API et envoyer une réponse HTTP.
from rest_framework.views import APIView
from rest_framework.response import Response
# Importe la base permettant de créer une permission personnalisée.
from rest_framework.permissions import BasePermission

# Définit les permissions nécessaires selon l'action effectuée sur une dépense.
class ExpensePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return request.user.has_perm("stock.view_expense")

        if request.method == "POST":
            return request.user.has_perm("stock.add_expense")

        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("stock.change_expense")

        if request.method == "DELETE":
            return request.user.has_perm("stock.delete_expense")

        return False

# Importe la permission qui exige qu'un utilisateur soit authentifié.
from rest_framework.permissions import IsAuthenticated

# Importe notre modèle Product et le serializer qui transforme les produits en données API.
from .models import Product, Expense
from .serializers import ProductSerializer, ExpenseSerializer


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

# Crée la vue API qui permet de consulter les dépenses et d'en créer une nouvelle.
class ExpenseListAPIView(APIView):
    permission_classes = [IsAuthenticated, ExpensePermission]

    # Traite les requêtes GET envoyées pour récupérer toutes les dépenses.
    def get(self, request):
        expenses = Expense.objects.all().order_by("-date", "-id")
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    # Traite les requêtes POST envoyées pour créer une nouvelle dépense.
    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)

        if serializer.is_valid():

            # Associe automatiquement la dépense à l'utilisateur connecté.
            serializer.save(created_by=request.user)

            return Response(serializer.data, status=201)

# Crée la vue API qui permet de consulter, modifier ou supprimer une dépense précise.
class ExpenseDetailAPIView(APIView):
    # Applique les permissions adaptées à chaque opération sur une dépense.
    permission_classes = [IsAuthenticated, ExpensePermission]

    # Traite les requêtes GET envoyées pour consulter une dépense.
    def get(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk)
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    # Traite les requêtes PUT envoyées pour modifier une dépense.
    def put(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk)
        serializer = ExpenseSerializer(expense, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # Traite les requêtes PATCH envoyées pour modifier partiellement une dépense.
    def patch(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk)
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # Traite les requêtes DELETE envoyées pour supprimer une dépense.
    def delete(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk)
        expense.delete()
        return Response(status=204)