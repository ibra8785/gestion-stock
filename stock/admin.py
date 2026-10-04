# Importe le système d'administration de Django.
from django.contrib import admin

# Importe les modèles que nous voulons gérer depuis Django Admin.
from .models import Product, Supplier, Customer, StockLot, Sale, SaleItem, SaleAllocation


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