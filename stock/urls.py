# Importe les fonctions permettant de définir les URLs de notre application.
from django.urls import path

# Importe les vues API utilisées pour gérer les produits et les dépenses.
from .views import ProductListAPIView, ProductDetailAPIView, SupplierListAPIView, SupplierDetailAPIView, CustomerListAPIView, CustomerDetailAPIView, StockEntryAPIView, StockAdjustmentAPIView, StockMovementListAPIView, SaleListCreateAPIView, ExpenseListAPIView, ExpenseDetailAPIView, DashboardAPIView, SalesReportAPIView, StockReportAPIView, ExpenseReportAPIView, ProfitReportAPIView


# Définit les routes disponibles pour les produits dans l'API.
urlpatterns = [
    # Retourne la liste de tous les produits et permet d'en créer un nouveau.
    path("products/", ProductListAPIView.as_view(), name="product-list"),

    # Retourne les informations d'un seul produit grâce à son identifiant.
    path("products/<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),

    # Retourne la liste des fournisseurs et permet d'en créer un nouveau.
    path("suppliers/", SupplierListAPIView.as_view(), name="supplier-list"),

    # Permet de consulter, modifier ou supprimer un fournisseur précis.
    path("suppliers/<int:pk>/", SupplierDetailAPIView.as_view(), name="supplier-detail"),

    # Retourne la liste des clients et permet d'en créer un nouveau.
    path("customers/", CustomerListAPIView.as_view(), name="customer-list"),

    # Permet de consulter, modifier ou supprimer un client précis.
    path("customers/<int:pk>/", CustomerDetailAPIView.as_view(), name="customer-detail"),

    # Permet d'enregistrer une nouvelle entrée de stock.
    path("stock/entries/", StockEntryAPIView.as_view(), name="stock-entry"),

    # Permet d'effectuer un ajustement sur un lot de stock.
    path("stock/adjustments/", StockAdjustmentAPIView.as_view(), name="stock-adjustment"),

    # Permet de consulter l'historique des mouvements de stock.
    path("stock/movements/", StockMovementListAPIView.as_view(), name="stock-movement-list"),

    # Permet de consulter les ventes et d'en créer une nouvelle.
    path("sales/", SaleListCreateAPIView.as_view(), name="sale-list-create"),

    # Retourne la liste des dépenses et permet d'en créer une nouvelle.
    path("expenses/", ExpenseListAPIView.as_view(), name="expense-list"),

    # Permet de consulter, modifier ou supprimer une dépense précise.
    path("expenses/<int:pk>/", ExpenseDetailAPIView.as_view(), name="expense-detail"),

    # Retourne les statistiques du tableau de bord.
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),

    # Retourne le rapport des ventes pour une période donnée.
    path("reports/sales/", SalesReportAPIView.as_view(), name="sales-report"),

    # Retourne le rapport du stock restant.
    path("reports/stock/", StockReportAPIView.as_view(), name="stock-report"),

    # Retourne le rapport des dépenses pour une période donnée.
    path("reports/expenses/", ExpenseReportAPIView.as_view(), name="expense-report"),

    # Retourne le rapport des bénéfices pour une période donnée.
    path("reports/profit/", ProfitReportAPIView.as_view(), name="profit-report"),
]