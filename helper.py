from classes.shop import *
from classes.player.main import Player
from classes.items.item import Item
import classes.items.materials as materials_module

import pygame

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

def draw_text_in_rect(
    surface: pygame.Surface,
    text: str,
    rect: pygame.Rect,
    *,
    font_name="robotomono",
    max_font_size=24,
    min_font_size=10,
    color=(0, 0, 255),
    padding=6,
    ellipsis=True,
    line_spacing=1.1,
    center=True
):
    """Draw text inside rect, wrapping and shrinking to fit. Returns final font size used."""
    inner_w = max(0, rect.width - 2*padding)
    inner_h = max(0, rect.height - 2*padding)

    if inner_w <= 0 or inner_h <= 0:
        return None

    def wrap_lines(font: pygame.font.Font, txt: str) -> list[str]:
        # Wrap by measuring candidate lines (word-based)
        words = txt.split()
        if not words:
            return []
        lines, cur = [], words[0]
        for w in words[1:]:
            test = cur + " " + w
            if font.size(test)[0] <= inner_w:
                cur = test
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        return lines

    fs = max_font_size
    chosen_lines = []
    chosen_font = None

    while fs >= min_font_size:
        f = pygame.font.SysFont(font_name, fs)
        lines = wrap_lines(f, text)

        # Measure total height
        line_h = f.get_linesize()
        total_h = int(line_h * line_spacing * len(lines))

        if total_h <= inner_h:
            chosen_lines = lines
            chosen_font = f
            break
        fs -= 1

    # If still too tall, we’ll truncate with ellipsis using the min size
    if chosen_font is None:
        chosen_font = pygame.font.SysFont(font_name, min_font_size)
        lines = wrap_lines(chosen_font, text)

        # Remove lines until it fits
        line_h = chosen_font.get_linesize()
        while lines and int(line_h * line_spacing * len(lines)) > inner_h:
            lines.pop()

        if lines and ellipsis:
            # Try to add ellipsis to the last line without exceeding width
            last = lines[-1]
            while last and chosen_font.size(last + "…")[0] > inner_w:
                last = last[:-1]
            lines[-1] = (last + "…") if last else "…"

        chosen_lines = lines

    # Render
    # Optional: draw a subtle background so text is readable
    # pygame.draw.rect(surface, (0, 0, 0, 80), rect)  # if using per-surface alpha

    # Clip to ensure no overflow ever shows
    prev_clip = surface.get_clip()
    surface.set_clip(rect)

    y = rect.y + padding
    # Vertical centering
    if center and chosen_lines:
        line_h = chosen_font.get_linesize()
        block_h = int(line_h * line_spacing * len(chosen_lines))
        y = rect.y + (rect.height - block_h) // 2

    for line in chosen_lines:
        img = chosen_font.render(line, True, color)
        if center:
            x = rect.x + (rect.width - img.get_width()) // 2
        else:
            x = rect.x + padding
        surface.blit(img, (x, y))
        y += int(chosen_font.get_linesize() * line_spacing)

    surface.set_clip(prev_clip)
    return chosen_font.get_height() if chosen_lines else None