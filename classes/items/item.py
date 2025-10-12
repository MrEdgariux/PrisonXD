from classes.items.materials import Material

class Item:
    def __init__(self, material: Material, quantity: int, metadata:dict = {}):
        self.material: Material = material
        self.quantity: int = quantity
        self.metadata: dict = metadata

    def __str__(self):
        return f"{self.material.name} x{self.quantity}"