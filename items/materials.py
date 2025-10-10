class Material:
    def __init__(self, id, name):
        self.id: str = id
        self.name: str = name

DIRT = Material("dirt", "Dirt")
STONE = Material("stone", "Stone")
WOOD = Material("wood", "Wood")
IRON = Material("iron", "Iron")
GOLD = Material("gold", "Gold")
DIAMOND = Material("diamond", "Diamond")

Materials: list = [
    DIRT,
    STONE,
    WOOD,
    IRON,
    GOLD,
    DIAMOND
]