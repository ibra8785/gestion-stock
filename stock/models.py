from django.db import models


# Modèle Product : permet de définir les informations
# que nous allons enregistrer pour chaque produit du stock.

class Product(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    format = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)

    # Définit le texte que Django doit afficher pour un produit dans les listes.
    def __str__(self):
        return f"{self.name} ({self.reference})"


# Modèle Supplier : permet d'enregistrer les informations
# de chaque fournisseur avec lequel nous travaillons.

class Supplier(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)

    # Définit le texte que Django doit afficher pour un fournisseur dans les listes.
    def __str__(self):
        return f"{self.name} ({self.reference})"


# Modèle StockLot : permet d'enregistrer chaque entrée de stock
# avec le produit, le fournisseur, la quantité, le prix d'achat
# et la date de réception.

# Modèle StockLot : permet d'enregistrer chaque entrée de stock
# avec le produit, le fournisseur, la quantité, le prix d'achat
# et la date de réception.

# Modèle Customer : permet d'enregistrer les informations
# de chaque client qui pourra être associé à une ou plusieurs ventes.

class Customer(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)

    # Définit le texte que Django doit afficher pour un client dans les listes.
    def __str__(self):
        return f"{self.name} ({self.reference})"

class StockLot(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    quantity_initial = models.PositiveIntegerField()
    quantity_remaining = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    date_received = models.DateTimeField(auto_now_add=True)

    # Calcule automatiquement la valeur totale du lot
    # à partir de la quantité initiale et du prix d'achat unitaire.
    @property
    def total_purchase_value(self):
        return self.quantity_initial * self.purchase_price

    # Lors de la création d'un nouveau lot, cette méthode initialise
    # automatiquement la quantité restante avec la quantité reçue.
    def save(self, *args, **kwargs):
        if self.pk is None:
            self.quantity_remaining = self.quantity_initial

        super().save(*args, **kwargs)

# Modèle Sale : permet d'enregistrer une vente complète,
# avec le client, la date, le montant total et le bénéfice total.

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ("ENTREE", "Entrée"),
        ("SORTIE", "Sortie"),
        ("AJUSTEMENT", "Ajustement"),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    stock_lot = models.ForeignKey(StockLot, on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)

class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

# Modèle SaleItem : représente un produit vendu dans une vente.
# Il enregistre la quantité vendue, le prix de vente et le coût d'achat.

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

# Modèle SaleAllocation : permet de préciser de quel lot de stock
# provient chaque quantité vendue lors d'une vente.

class SaleAllocation(models.Model):
    sale_item = models.ForeignKey(SaleItem, on_delete=models.CASCADE)
    stock_lot = models.ForeignKey(StockLot, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)