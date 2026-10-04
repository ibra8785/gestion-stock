from django.db import transaction

# Importe les modèles nécessaires pour calculer les ventes,
# créer leurs lignes et enregistrer les lots utilisés.
from .models import StockLot, Sale, SaleItem, SaleAllocation

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

# Déduit les quantités vendues des lots de stock
# en respectant l'ordre FIFO.
def apply_fifo_sale(allocations):
    for allocation in allocations:
        lot = allocation["lot"]
        quantity = allocation["quantity"]

        if quantity > lot.quantity_remaining:
            raise ValueError("Impossible de retirer plus de stock que la quantité disponible.")

        lot.quantity_remaining -= quantity
        lot.save(update_fields=["quantity_remaining"])

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