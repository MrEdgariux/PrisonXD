import pygame
from classes.items.item import Item

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, item: Item):
        super().__init__()

        if (not item.metadata.get("decoration", False)) and (x % 50 != 0 or y % 50 != 0):
            raise ValueError(f"Block position must be aligned to a 50x50 grid. Got ({x}, {y})")
        self.image = pygame.Surface((width, height))
        self.image.fill(item.material.color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.item = item

    def get_drops(self) -> Item:
        return self.item
