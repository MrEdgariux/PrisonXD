from classes.shop import Shop, ShopItem, ShopManager
from typing import List

from classes.items.materials import *

def GameInit(shop_manager: ShopManager):
    ShopItems = [
        ShopItem(DIRT, buy_price=0, sell_price=1, max_stock=-1),
        ShopItem(STONE, buy_price=0, sell_price=1, max_stock=-1),
        ShopItem(GRASS, buy_price=0, sell_price=1, max_stock=-1),
        ShopItem(WOOD, buy_price=0, sell_price=2, max_stock=-1),
        ShopItem(IRON, buy_price=0, sell_price=3, max_stock=-1),
        ShopItem(GOLD, buy_price=0, sell_price=10, max_stock=-1),
        ShopItem(DIAMOND, buy_price=0, sell_price=50, max_stock=-1)
    ]

    shop = Shop("mine_sell_shop", "Sell Items", ShopItems)
    shop_manager.register(shop)