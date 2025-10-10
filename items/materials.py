class Material:
    def __init__(self, id, name, color=(255, 0, 255)):
        self.id: str = id
        self.name: str = name
        self.color: tuple[int, int, int] = color

DIRT = Material("dirt", "Dirt", (139, 69, 19))  # Brown
GRASS = Material("grass", "Grass", (34, 139, 34))  # Green
STONE = Material("stone", "Stone", (128, 128, 128))  # Gray
WOOD = Material("wood", "Wood", (160, 82, 45))  # Sienna
IRON = Material("iron", "Iron", (192, 192, 192))  # Silver
GOLD = Material("gold", "Gold", (255, 215, 0))  # Gold
DIAMOND = Material("diamond", "Diamond", (0, 255, 255))  # Cyan

BEDROCK = Material("bedrock", "Bedrock", (0, 0, 0))  # Black, indestructible

Materials: list = [
    DIRT,
    GRASS,
    STONE,
    WOOD,
    IRON,
    GOLD,
    DIAMOND
]