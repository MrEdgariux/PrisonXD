from typing import List

from classes.chat.commands.command_handler import CommandRegistry, CommandContext

def cmd_help(ctx: CommandContext, args: List[str]):
    lines = [
        "Commands:",
        "/help",
        "/say <text>",
        "/money                - show balance",
        "/give <item_id> <n>   - add items",
        "/tp <x> <y>           - teleport player",
        "/scene <name>         - switch scene (hub|mine|shop)",
        "/shop                 - open shop (if in Shop scene)",
        "/inv                  - toggle inventory",
        "/debug                - toggle F3 overlay",
    ]
    for ln in lines:
        ctx.chat.add_message("Help", ln)

def cmd_say(ctx: CommandContext, args: List[str]):
    ctx.chat.add_message("You", " ".join(args) if args else "")

def cmd_money(ctx: CommandContext, args: List[str]):
    bal = getattr(ctx.player, "balance", 0)
    ctx.notifier.push(f"Balance: ${bal}", level="info")

def cmd_give(ctx: CommandContext, args: List[str]):
    if len(args) < 2:
        raise ValueError("Usage: /give <item_id> <qty>")
    item_id = args[0]
    qty = int(args[1])
    # Your factory:
    from classes.items.item import Item
    from classes.items.materials import Materials
    mat = None
    for material in Materials:
        if material.name.upper() == item_id.upper() or material.id.upper() == item_id.upper():
            mat = material
            break
    if not mat:
        raise ValueError(f"Unknown item '{item_id}'")
    item = Item(mat, qty)
    ok, _ = ctx.player.inventory.add_item(item)
    if ok:
        ctx.notifier.push(f"Gave {mat.name} x{qty}", level="success")
    else:
        ctx.notifier.push("Inventory full", level="warning")

def cmd_tp(ctx: CommandContext, args: List[str]):
    if len(args) < 2:
        raise ValueError("Usage: /tp <x> <y>")
    x, y = int(args[0]), int(args[1])
    ctx.player.position = (x, y)
    ctx.notifier.push(f"Teleported to ({x}, {y})", level="success")

def cmd_scene(ctx: CommandContext, args: List[str]):
    if not args:
        raise ValueError("Usage: /scene <hub|mine|shop>")
    name = args[0]
    ctx.scene_mgr.set(name, ctx.player)
    ctx.notifier.push(f"Switched scene to {name}", level="success")

def cmd_shop(ctx: CommandContext, args: List[str]):
    if ctx.shop_ui and ctx.scene_mgr.current and getattr(ctx.scene_mgr.current, "shop", None):
        ctx.shop_ui.open(ctx.scene_mgr.current.shop, ctx.player)
        ctx.notifier.push("Shop opened", level="info")
    else:
        ctx.notifier.push("No shop here.", level="warning")

