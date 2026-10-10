# Importe les outils de Django REST Framework et le modèle Product que notre API devra exposer.
from rest_framework import serializers

from .models import Product, Supplier, Customer, Expense, Sale, StockLot, StockMovement

# Définit le serializer du produit afin de convertir les données du modèle Product en données utilisables par notre API.
class ProductSerializer(serializers.ModelSerializer):
    # Configure le serializer pour utiliser le modèle Product et tous ses champs.
    class Meta:
        model = Product
        fields = "__all__"

# Définit le serializer du fournisseur afin de convertir les données du modèle Supplier pour l'API.
class SupplierSerializer(serializers.ModelSerializer):
    # Configure le serializer pour utiliser le modèle Supplier et tous ses champs.
    class Meta:
        model = Supplier
        fields = "__all__"

# Définit le serializer du client afin de convertir les données du modèle Customer pour l'API.
class CustomerSerializer(serializers.ModelSerializer):
    # Configure le serializer pour utiliser le modèle Customer et tous ses champs.
    class Meta:
        model = Customer
        fields = "__all__"

# Définit les données nécessaires pour enregistrer une nouvelle entrée de stock.
class StockEntrySerializer(serializers.Serializer):
    # Identifie le produit qui entre en stock.
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    # Identifie le fournisseur de l'entrée de stock.
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all()
    )

    # Quantité reçue lors de l'entrée en stock.
    quantity = serializers.IntegerField(min_value=1)

    # Prix d'achat unitaire du produit.
    purchase_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )

    # Motif facultatif de l'entrée de stock.
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="Réception de stock",
    )

# Définit les données nécessaires pour effectuer un ajustement de stock.
class StockAdjustmentSerializer(serializers.Serializer):
    # Identifie le lot de stock à ajuster.
    stock_lot = serializers.PrimaryKeyRelatedField(
        queryset=StockLot.objects.all()
    )

    # Quantité à ajouter ou à retirer du stock.
    quantity = serializers.IntegerField()

    # Motif obligatoire de l'ajustement.
    reason = serializers.CharField()

# Définit le serializer des dépenses afin de convertir les données du modèle Expense pour l'API.
class ExpenseSerializer(serializers.ModelSerializer):
    # Configure le serializer pour utiliser le modèle Expense et tous ses champs.
    class Meta:
        model = Expense
        fields = "__all__"

        # Empêche le client de modifier l'utilisateur ayant créé la dépense.
        read_only_fields = ("created_by",)

# Définit le serializer utilisé pour retourner les informations nécessaires au rapport des ventes.
class SalesReportSerializer(serializers.ModelSerializer):
    # Affiche le nom du client associé à la vente.
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Sale
        fields = (
            "id",
            "date",
            "customer_name",
            "total_amount",
            "total_profit",
        )

# Définit le serializer utilisé pour retourner les informations nécessaires au rapport du stock.
class StockReportSerializer(serializers.ModelSerializer):
    # Affiche la référence du produit.
    product_reference = serializers.CharField(source="product.reference", read_only=True)

    # Affiche le nom du produit.
    product_name = serializers.CharField(source="product.name", read_only=True)

    # Affiche le nom du fournisseur.
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    # Calcule la valeur du stock restant pour le lot.
    stock_value = serializers.SerializerMethodField()

    # Calcule la valeur du stock restant à partir de la quantité et du prix d'achat.
    def get_stock_value(self, obj):
        return obj.quantity_remaining * obj.purchase_price

    class Meta:
        model = StockLot
        fields = (
            "id",
            "product_reference",
            "product_name",
            "supplier_name",
            "quantity_remaining",
            "purchase_price",
            "stock_value",
            "date_received",
        )

# Définit le serializer utilisé pour retourner les informations nécessaires au rapport des dépenses.
class ExpenseReportSerializer(serializers.ModelSerializer):
    # Affiche le nom de l'utilisateur qui a enregistré la dépense.
    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = Expense
        fields = (
            "id",
            "label",
            "category",
            "amount",
            "date",
            "description",
            "created_by_username",
        )

# Définit le serializer utilisé pour retourner les informations du rapport des bénéfices.
class ProfitReportSerializer(serializers.Serializer):
    # Chiffre d'affaires réalisé pendant la période.
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)

    # Bénéfice brut généré par les ventes.
    total_profit = serializers.DecimalField(max_digits=12, decimal_places=2)

    # Total des dépenses de la période.
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)

    # Bénéfice net après déduction des dépenses.
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2)

# Définit le serializer des mouvements de stock pour permettre leur consultation via l'API.
class StockMovementSerializer(serializers.ModelSerializer):
    # Affiche le nom du produit concerné par le mouvement.
    product_name = serializers.CharField(source="product.name", read_only=True)

    # Affiche la référence du produit concerné par le mouvement.
    product_reference = serializers.CharField(source="product.reference", read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "product",
            "product_name",
            "product_reference",
            "stock_lot",
            "movement_type",
            "quantity",
            "reason",
            "date",
        ]

# Définit les données nécessaires pour ajouter un produit dans une vente.
class SaleItemCreateSerializer(serializers.Serializer):
    # Identifie le produit vendu.
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    # Définit la quantité vendue.
    quantity = serializers.IntegerField(min_value=1)

    # Définit le prix de vente unitaire.
    selling_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )


# Définit les données nécessaires pour créer une vente complète.
class SaleCreateSerializer(serializers.Serializer):
    # Identifie le client associé à la vente.
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all()
    )

    # Contient les différents produits de la vente.
    items = SaleItemCreateSerializer(many=True, allow_empty=False)