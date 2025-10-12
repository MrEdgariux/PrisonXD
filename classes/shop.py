# shop.py
from dataclasses import dataclass
from typing import List, Dict

from classes.items.materials import Material

@dataclass
class ShopItem:
    material: Material
    buy_price: int
    sell_price: int
    max_stock: int = -1

class Shop:
    def __init__(self, shop_id: str, display_name: str, items: List[ShopItem]):
        self.id = shop_id
        self.display_name = display_name
        self.items = items
        self.stock = {it.material.id: it.max_stock for it in items if it.max_stock >= 0}

class ShopManager:
    def __init__(self):
        self.shops: Dict[str, Shop] = {}

    def register(self, shop: Shop):
        self.shops[shop.id] = shop

    def get(self, shop_id: str) -> Shop:
        return self.shops.get(shop_id)
