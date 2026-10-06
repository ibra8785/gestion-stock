# Importe le système d'administration de Django.
from django.contrib import admin

# Importe les modèles disponibles dans l'administration Django.
from .models import Product, Supplier, Customer, StockLot, StockMovement, Sale, SaleItem, SaleAllocation


# Personnalise l'affichage des lots de stock dans Django Admin.
# Nous affichons les informations importantes du lot,
# notamment sa valeur totale calculée automatiquement.

@admin.register(StockLot)
class StockLotAdmin(admin.ModelAdmin):
    # Affiche les informations importantes dans la liste des lots.
    list_display = (
        "product",
        "supplier",
        "quantity_initial",
        "quantity_remaining",
        "purchase_price",
        "total_purchase_value",
        "date_received",
    )

    # Masque la quantité restante dans le formulaire,
    # car elle sera calculée automatiquement par le modèle.
    exclude = ("quantity_remaining",)


admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(SaleAllocation)

# Personnalise l'affichage de l'historique des mouvements de stock.
@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    # Affiche les informations essentielles du mouvement dans la liste.
    list_display = (
        "product",
        "stock_lot",
        "movement_type",
        "quantity",
        "reason",
        "date",
    )

    # Permet de filtrer rapidement les mouvements par type.
    list_filter = ("movement_type", "date")

    # Permet de rechercher par produit, lot ou raison.
    search_fields = ("product__reference", "stock_lot__id", "reason")