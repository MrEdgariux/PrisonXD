from classes.shop import *
from classes.player.main import Player
from classes.items.item import Item
import classes.items.materials as materials_module

# try to create an Item from an item_id (string like "dirt" or "DIRT" or "stone")
def generate_item_from_id(item_id: str, qty: int = 1):
    material = None
    for mat in materials_module.Materials:
        if mat.id.lower() == item_id.lower():
            material = mat
            break
    if not material:
        raise ValueError(f"Unknown material ID '{item_id}'")
    return Item(material, qty)

def process_shop_action(player: Player, shop: Shop, action_tuple, notifier):
    """
    action_tuple = (action, item_id, qty)
    action in ("buy","sell")
    notifier: your NotificationManager instance to push messages
    """
    if not action_tuple:
        return
    act, item_id, qty = action_tuple
    qty = max(1, int(qty))

    shop_item = next((i for i in shop.items if i.material.id == item_id), None)
    if not shop_item:
        notifier.push("Shop item not found", level="error")
        return

    # BUY
    if act == "buy":
        total_price = shop_item.buy_price * qty
        if not player.deduct_money(total_price):
            notifier.push("Not enough money!", level="warning")
            return

        # create Item instance(s)
        try:
            to_add = generate_item_from_id(item_id, qty)
        except ValueError:
            player.add_money(total_price)  # refund
            notifier.push("Item not recognized, purchase cancelled.", level="error")
            return

        # Try to add to inventory; adapt to either add_item signature:
        try:
            success, returned = player.inventory.add_item(to_add)
        except TypeError:
            # maybe inventory expects a list of Item or different shape; try list
            try:
                success, returned = player.inventory.add_item([to_add])
            except Exception as e:
                # give back money and notify
                player.add_money(total_price)
                notifier.push("Failed to add item to inventory.", level="error")
                return

        if not success:
            # `returned` may be leftover item(s) — try to compute refund
            # best-effort: if returned has .quantity attribute
            refund_qty = 0
            if hasattr(returned, "quantity"):
                refund_qty = returned.quantity
            elif isinstance(returned, list) and returned and hasattr(returned[0], "quantity"):
                refund_qty = returned[0].quantity
            refund_amount = refund_qty * shop_item.buy_price
            if refund_amount:
                player.add_money(refund_amount)
                notifier.push(f"Inventory full — refunded {refund_qty} item(s).", level="warning")
            else:
                notifier.push("Inventory full — purchase failed.", level="warning")
            return

        # success
        # optionally decrement shop stock if present
        if hasattr(shop, "stock") and item_id in getattr(shop, "stock", {}):
            if shop.stock[item_id] > 0:
                shop.stock[item_id] = max(0, shop.stock[item_id] - qty)

        notifier.push(f"Bought {shop_item.name} x{qty} - {total_price}$", level="success")

    # SELL
    elif act == "sell":
        try:
            to_sell = generate_item_from_id(item_id, qty)
        except ValueError:
            notifier.push("Unknown item to sell.", level="error")
            return

        # Try to remove from inventory. We expect remove_item to accept an Item or similar
        try:
            success, remaining = player.inventory.remove_item(to_sell)
        except TypeError:
            try:
                success, remaining = player.inventory.remove_item([to_sell])
            except Exception:
                notifier.push("Could not remove item from inventory.", level="error")
                return

        if not success:
            notifier.push("You don't have that item to sell.", level="warning")
            return

        earned = shop_item.sell_price * qty
        player.add_money(earned)

        # increase shop stock if present
        if hasattr(shop, "stock") and item_id in getattr(shop, "stock", {}):
            shop.stock[item_id] += qty

        notifier.push(f"Sold {shop_item.material.name} x{qty} +{earned}$", level="success")