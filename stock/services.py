from django.db import transaction

# Importe les outils nécessaires aux calculs statistiques du tableau de bord.
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper

# Importe les modèles utilisés par les services de gestion du stock, des ventes et des dépenses.
from .models import StockLot, Sale, SaleItem, SaleAllocation, StockMovement, Expense

# Parcourt les lots disponibles dans l'ordre FIFO
# afin de déterminer quelle quantité doit être prélevée dans chaque lot.
def get_fifo_lots(product, quantity_needed):
    # Vérifie que la quantité demandée est strictement supérieure à zéro.
    if quantity_needed <= 0:
        raise ValueError("La quantité à vendre doit être supérieure à zéro.")

    lots = StockLot.objects.filter(
        product=product,
        quantity_remaining__gt=0
    ).order_by("date_received", "id")

    allocations = []
    remaining_quantity = quantity_needed

    for lot in lots:
        if remaining_quantity <= 0:
            break

        quantity_to_take = min(
            lot.quantity_remaining,
            remaining_quantity
        )

        allocations.append({
            "lot": lot,
            "quantity": quantity_to_take,
            "cost_price": lot.purchase_price,
        })

        remaining_quantity -= quantity_to_take

    # Vérifie que les lots disponibles permettent de couvrir toute la quantité demandée.
    if remaining_quantity > 0:
        raise ValueError("Stock insuffisant pour effectuer cette opération.")

    return allocations

# Calcule le chiffre d'affaires, le coût d'achat réel
# et le bénéfice d'une vente en utilisant les lots FIFO.
def calculate_sale(product, quantity, selling_price):
    allocations = get_fifo_lots(product, quantity)

    total_cost = 0

    for allocation in allocations:
        total_cost += (
            allocation["quantity"]
            * allocation["cost_price"]
        )

    total_amount = quantity * selling_price
    total_profit = total_amount - total_cost

    return {
        "allocations": allocations,
        "total_cost": total_cost,
        "total_amount": total_amount,
        "total_profit": total_profit,
    }

# Retire les quantités vendues des lots et enregistre chaque sortie de stock.
def apply_fifo_sale(allocations):
    for allocation in allocations:
        lot = allocation["lot"]
        quantity = allocation["quantity"]

        if quantity > lot.quantity_remaining:
            raise ValueError("Impossible de retirer plus de stock que la quantité disponible.")

        lot.quantity_remaining -= quantity
        lot.save(update_fields=["quantity_remaining"])

        # Enregistre la quantité réellement sortie du lot à cause de la vente.
        StockMovement.objects.create(
            product=lot.product,
            stock_lot=lot,
            movement_type="SORTIE",
            quantity=quantity,
            reason="Vente",
        )

# Crée un lot de stock et enregistre automatiquement son entrée dans l'historique.
def create_stock_entry(product, supplier, quantity, purchase_price, reason="Réception de stock"):
    with transaction.atomic():
        lot = StockLot.objects.create(
            product=product,
            supplier=supplier,
            quantity_initial=quantity,
            quantity_remaining=quantity,
            purchase_price=purchase_price,
        )

        StockMovement.objects.create(
            product=product,
            stock_lot=lot,
            movement_type="ENTREE",
            quantity=quantity,
            reason=reason,
        )

        return lot

# Ajuste la quantité restante d'un lot et enregistre la correction dans l'historique.
def adjust_stock(lot, quantity, reason):
    with transaction.atomic():
        new_quantity = lot.quantity_remaining + quantity

        if new_quantity < 0:
            raise ValueError("L'ajustement ne peut pas rendre le stock négatif.")

        lot.quantity_remaining = new_quantity
        lot.save(update_fields=["quantity_remaining"])

        StockMovement.objects.create(
            product=lot.product,
            stock_lot=lot,
            movement_type="AJUSTEMENT",
            quantity=abs(quantity),
            reason=reason,
        )

        return lot

# Crée une vente, sa ligne de produit et les allocations
# puis déduit les quantités des lots utilisés par le système FIFO.
def create_sale(customer, product, quantity, selling_price):
    with transaction.atomic():
        result = calculate_sale(
            product,
            quantity,
            selling_price
        )

        sale = Sale.objects.create(
            customer=customer,
            total_amount=result["total_amount"],
            total_profit=result["total_profit"],
        )

        sale_item = SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            selling_price=selling_price,
            cost_price=result["total_cost"] / quantity,
            profit=result["total_profit"],
        )

        for allocation in result["allocations"]:
            SaleAllocation.objects.create(
                sale_item=sale_item,
                stock_lot=allocation["lot"],
                quantity=allocation["quantity"],
                cost_price=allocation["cost_price"],
            )

        apply_fifo_sale(result["allocations"])

        return sale

# Crée une vente contenant plusieurs produits
# en appliquant le système FIFO à chaque produit.
def create_multi_product_sale(customer, items):
    # Vérifie qu'une vente contient au moins un produit.
    if not items:
        raise ValueError("Une vente doit contenir au moins un produit.")
    product_ids = [item["product"].id for item in items]

    # Vérifie qu'un même produit n'apparaît pas plusieurs fois dans la même vente.
    if len(product_ids) != len(set(product_ids)):
        raise ValueError("Un même produit ne peut pas apparaître plusieurs fois dans une vente.")
    
    with transaction.atomic():
        total_amount = 0
        total_profit = 0

        sale = Sale.objects.create(
            customer=customer,
            total_amount=0,
            total_profit=0,
        )

        for item in items:
            product = item["product"]
            quantity = item["quantity"]
            selling_price = item["selling_price"]

            result = calculate_sale(
                product,
                quantity,
                selling_price
            )

            sale_item = SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                selling_price=selling_price,
                cost_price=result["total_cost"] / quantity,
                profit=result["total_profit"],
            )

            for allocation in result["allocations"]:
                SaleAllocation.objects.create(
                    sale_item=sale_item,
                    stock_lot=allocation["lot"],
                    quantity=allocation["quantity"],
                    cost_price=allocation["cost_price"],
                )

            apply_fifo_sale(result["allocations"])

            total_amount += result["total_amount"]
            total_profit += result["total_profit"]

        sale.total_amount = total_amount
        sale.total_profit = total_profit
        sale.save(update_fields=["total_amount", "total_profit"])

        return sale

# Crée une dépense et l'associe à l'utilisateur qui l'a enregistrée.
def create_expense(
    label,
    category,
    amount,
    date,
    created_by,
    description="",
):
    # Vérifie que le montant est strictement supérieur à zéro.
    if amount <= 0:
        raise ValueError("Le montant de la dépense doit être supérieur à zéro.")

    # Crée la dépense dans une transaction atomique.
    with transaction.atomic():
        expense = Expense.objects.create(
            label=label,
            category=category,
            amount=amount,
            date=date,
            description=description,
            created_by=created_by,
        )

        return expense

# Calcule les principaux indicateurs du tableau de bord.
def get_dashboard_statistics():
    # Calcule les indicateurs financiers liés aux ventes.
    total_sales = Sale.objects.aggregate(total=Sum("total_amount"))["total"] or 0
    total_profit = Sale.objects.aggregate(total=Sum("total_profit"))["total"] or 0

    # Calcule le montant total des dépenses.
    total_expenses = Expense.objects.aggregate(total=Sum("amount"))["total"] or 0

    # Calcule le bénéfice net après déduction des dépenses.
    net_profit = total_profit - total_expenses

    # Compte le nombre total de ventes enregistrées.
    sales_count = Sale.objects.aggregate(total=Count("id"))["total"]

    # Calcule la quantité totale actuellement disponible en stock.
    stock_quantity = StockLot.objects.aggregate(total=Sum("quantity_remaining"))["total"] or 0

    # Calcule la valeur du stock restant au prix d'achat.
    stock_value = StockLot.objects.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("quantity_remaining") * F("purchase_price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
    )["total"] or 0

    # Calcule les quantités vendues pour chaque produit.
    top_products = list(
        SaleItem.objects.values("product__reference", "product__name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")
    )

    # Calcule le montant total des dépenses pour chaque catégorie.
    expense_distribution = list(
        Expense.objects
        .values("category")
        .annotate(total_amount=Sum("amount"))
        .order_by("-total_amount")
    )

    # Retourne toutes les statistiques du tableau de bord.
    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "sales_count": sales_count,
        "stock_quantity": stock_quantity,
        "stock_value": stock_value,
        "top_products": top_products,
        "expense_distribution": expense_distribution,
    }