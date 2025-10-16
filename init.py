from classes.shop import Shop, ShopItem, ShopManager

from classes.items.materials import *
from classes.player.ranks import Rank, RankManager
from classes.chat.commands.command_handler import CommandRegistry, CommandContext

from commands_init import *

def GameInit(shop_manager: ShopManager, rank_manager: RankManager, reg: CommandRegistry):
    
    ShopItems = [
        ShopItem(DIRT, buy_price=0, sell_price=1, max_stock=-1),
        ShopItem(STONE, buy_price=0, sell_price=1, max_stock=-1),
        ShopItem(GRASS, buy_price=0, sell_price=1, max_stock=-1),
        ShopItem(WOOD, buy_price=0, sell_price=2, max_stock=-1),
        ShopItem(IRON, buy_price=0, sell_price=3, max_stock=-1),
        ShopItem(GOLD, buy_price=0, sell_price=10, max_stock=-1),
        ShopItem(DIAMOND, buy_price=0, sell_price=50, max_stock=-1)
    ]

    Ranks = [
        Rank("c", "C", 0, (150, 150, 150)),
        Rank("b", "B", 100, (100, 100, 255)),
        Rank("a", "A", 500, (255, 100, 100)),
        Rank("elitas", "Elitas", 2000, (255, 255, 100)),
        Rank("laisvas", "Laisvas", 5000, (100, 255, 100)),
    ]

    for rank in Ranks:
        rank_manager.register(rank)

    shop = Shop("mine_sell_shop", "Sell Items", ShopItems)
    shop_manager.register(shop)

    reg.register("help",  cmd_help)
    reg.register("say",   cmd_say)
    reg.register("money", cmd_money)
    reg.register("give",  cmd_give, aliases=["item"])
    reg.register("tp",    cmd_tp,   aliases=["teleport"])
    reg.register("scene", cmd_scene)
    reg.register("shop",  cmd_shop)