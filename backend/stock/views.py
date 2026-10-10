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
from .models import Product, Supplier, Customer, Expense, StockMovement, Sale

from .serializers import ProductSerializer, SupplierSerializer, CustomerSerializer, StockEntrySerializer, StockAdjustmentSerializer, StockMovementSerializer, SaleCreateSerializer, ExpenseSerializer, SalesReportSerializer, StockReportSerializer, ExpenseReportSerializer, ProfitReportSerializer

# Importe la fonction qui calcule les statistiques du tableau de bord.
from .services import create_stock_entry, adjust_stock, create_multi_product_sale, get_dashboard_statistics, get_sales_report, get_stock_report, get_expenses_report, get_profit_report

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

# Crée la vue API qui permet de lister et créer les fournisseurs.
class SupplierListAPIView(APIView):
    # Réserve l'accès aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # GET : retourne la liste de tous les fournisseurs.
    def get(self, request):
        suppliers = Supplier.objects.all().order_by("name")
        serializer = SupplierSerializer(suppliers, many=True)

        return Response(serializer.data)

    # POST : crée un nouveau fournisseur.
    def post(self, request):
        serializer = SupplierSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# Crée la vue API qui permet de consulter, modifier et supprimer un fournisseur.
class SupplierDetailAPIView(APIView):
    # Réserve l'accès aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # GET : retourne les informations d'un fournisseur précis.
    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        serializer = SupplierSerializer(supplier)

        return Response(serializer.data)

    # PUT : remplace les informations d'un fournisseur précis.
    def put(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        serializer = SupplierSerializer(supplier, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # PATCH : modifie partiellement les informations d'un fournisseur.
    def patch(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        serializer = SupplierSerializer(
            supplier,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # DELETE : supprime un fournisseur précis.
    def delete(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.delete()

        return Response(status=204)

# Crée la vue API qui permet de lister et créer les clients.
class CustomerListAPIView(APIView):
    # Réserve l'accès aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # GET : retourne la liste de tous les clients.
    def get(self, request):
        customers = Customer.objects.all().order_by("name")
        serializer = CustomerSerializer(customers, many=True)

        return Response(serializer.data)

    # POST : crée un nouveau client.
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# Crée la vue API qui permet de consulter, modifier et supprimer un client.
class CustomerDetailAPIView(APIView):
    # Réserve l'accès aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # GET : retourne les informations d'un client précis.
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer)

        return Response(serializer.data)

    # PUT : remplace les informations d'un client précis.
    def put(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # PATCH : modifie partiellement les informations d'un client.
    def patch(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(
            customer,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # DELETE : supprime un client précis.
    def delete(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()

        return Response(status=204)

# Crée la vue API qui permet d'enregistrer une nouvelle entrée de stock.
class StockEntryAPIView(APIView):
    # Réserve l'accès aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # POST : enregistre une nouvelle entrée de stock.
    def post(self, request):
        serializer = StockEntrySerializer(data=request.data)

        if serializer.is_valid():
            lot = create_stock_entry(
                product=serializer.validated_data["product"],
                supplier=serializer.validated_data["supplier"],
                quantity=serializer.validated_data["quantity"],
                purchase_price=serializer.validated_data["purchase_price"],
                reason=serializer.validated_data["reason"],
            )

            return Response(
                {
                    "id": lot.id,
                    "product": lot.product.id,
                    "supplier": lot.supplier.id,
                    "quantity_initial": lot.quantity_initial,
                    "quantity_remaining": lot.quantity_remaining,
                    "purchase_price": lot.purchase_price,
                    "date_received": lot.date_received,
                },
                status=201,
            )

        return Response(serializer.errors, status=400)

# Crée la vue API qui permet d'effectuer un ajustement de stock.
class StockAdjustmentAPIView(APIView):
    # Réserve l'accès aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # POST : applique un ajustement sur un lot de stock.
    def post(self, request):
        serializer = StockAdjustmentSerializer(data=request.data)

        if serializer.is_valid():
            try:
                lot = adjust_stock(
                    lot=serializer.validated_data["stock_lot"],
                    quantity=serializer.validated_data["quantity"],
                    reason=serializer.validated_data["reason"],
                )
            except ValueError as error:
                return Response(
                    {"error": str(error)},
                    status=400,
                )

            return Response(
                {
                    "id": lot.id,
                    "product": lot.product.id,
                    "quantity_remaining": lot.quantity_remaining,
                    "purchase_price": lot.purchase_price,
                }
            )

        return Response(serializer.errors, status=400)

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

# Crée la vue API qui retourne les statistiques du tableau de bord.
class DashboardAPIView(APIView):
    # Réserve l'accès au tableau de bord aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # Traite les requêtes GET pour récupérer les statistiques.
    def get(self, request):
        statistics = get_dashboard_statistics()
        return Response(statistics)

# Crée la vue API qui retourne le rapport des ventes pour une période donnée.
class SalesReportAPIView(APIView):
    # Réserve l'accès au rapport aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # GET : récupère les ventes comprises entre deux dates.
    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not start_date or not end_date:
            return Response(
                {"error": "Les paramètres start_date et end_date sont obligatoires."},
                status=400,
            )

        sales = get_sales_report(start_date, end_date)
        serializer = SalesReportSerializer(sales, many=True)

        return Response(serializer.data)

# Crée la vue API qui retourne le rapport du stock restant.
class StockReportAPIView(APIView):
    # Réserve l'accès au rapport aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # GET : récupère les lots de stock encore disponibles.
    def get(self, request):
        stock_lots = get_stock_report()
        serializer = StockReportSerializer(stock_lots, many=True)

        return Response(serializer.data)

# Crée la vue API qui retourne le rapport des dépenses pour une période donnée.
class ExpenseReportAPIView(APIView):
    # Réserve l'accès au rapport aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # GET : récupère les dépenses comprises entre deux dates.
    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not start_date or not end_date:
            return Response(
                {"error": "Les paramètres start_date et end_date sont obligatoires."},
                status=400,
            )

        expenses = get_expenses_report(start_date, end_date)
        serializer = ExpenseReportSerializer(expenses, many=True)

        return Response(serializer.data)

# Crée la vue API qui retourne le rapport des bénéfices pour une période donnée.
class ProfitReportAPIView(APIView):
    # Réserve l'accès au rapport aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # GET : récupère les résultats financiers entre deux dates.
    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not start_date or not end_date:
            return Response(
                {"error": "Les paramètres start_date et end_date sont obligatoires."},
                status=400,
            )

        profit_report = get_profit_report(start_date, end_date)
        serializer = ProfitReportSerializer(profit_report)

        return Response(serializer.data)

# Crée la vue API qui permet de consulter l'historique des mouvements de stock.
class StockMovementListAPIView(APIView):
    # Réserve l'accès aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # GET : retourne tous les mouvements de stock du plus récent au plus ancien.
    def get(self, request):
        movements = StockMovement.objects.select_related(
            "product",
            "stock_lot",
        ).order_by("-date")

        serializer = StockMovementSerializer(movements, many=True)

        return Response(serializer.data)

# Crée la vue API qui permet d'enregistrer une nouvelle vente.
class SaleListCreateAPIView(APIView):
    # Réserve l'accès aux utilisateurs connectés.
    permission_classes = [IsAuthenticated]

    # POST : crée une nouvelle vente avec un ou plusieurs produits.
    def post(self, request):
        serializer = SaleCreateSerializer(data=request.data)

        if serializer.is_valid():
            try:
                sale = create_multi_product_sale(
                    customer=serializer.validated_data["customer"],
                    items=serializer.validated_data["items"],
                )
            except ValueError as error:
                return Response(
                    {"error": str(error)},
                    status=400,
                )

            return Response(
                {
                    "id": sale.id,
                    "customer": sale.customer.id,
                    "total_amount": sale.total_amount,
                    "total_profit": sale.total_profit,
                    "date": sale.date,
                },
                status=201,
            )

        return Response(serializer.errors, status=400)

    # GET : retourne la liste des ventes les plus récentes.
    def get(self, request):
        sales = Sale.objects.select_related("customer").order_by("-date")

        return Response(
            [
                {
                    "id": sale.id,
                    "customer": sale.customer.id,
                    "customer_name": sale.customer.name,
                    "total_amount": sale.total_amount,
                    "total_profit": sale.total_profit,
                    "date": sale.date,
                }
                for sale in sales
            ]
        )