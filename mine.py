import pygame
from items.item import Item

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, item: Item):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.item = item

    def get_drops(self) -> Item:
        return self.item
