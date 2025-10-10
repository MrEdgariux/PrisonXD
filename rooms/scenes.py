import pygame, math, random, configparser
from mine import Block

from items.materials import *
from items.item import Item

class SceneBase:
    def __init__(self, name, spawn=(100,100)):
        self.name = name
        self.spawn = spawn
        self.config = configparser.ConfigParser()
        self.settings = configparser.ConfigParser()
        self.cubes: list[Block] = []
        self.portals = []  # list of (rect, target_scene_name, target_spawn)

        self.config.read('config.ini')
        self.settings.read('settings.ini')

    def load(self):
        """(Re)create blocks/portals for this scene."""
        pass

    def draw(self, screen):
        for cube in self.cubes:
            screen.blit(cube.image, cube.rect)
        # (Optional) visualize portals for debugging
        for r, *_ in self.portals: pygame.draw.rect(screen, (0,125,125), r, 2)

        # A title at the top
        font = pygame.font.SysFont(None, 36)
        text = font.render(self.name.upper(), True, (255, 255, 255))
        screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 10))

    def update(self, player):
        """Return (next_scene_name, next_spawn) if a portal is touched, else (None, None)."""
        px, py = player.position
        cube_size = int(self.config.get('game.mines', 'block_size', fallback=50))
        
        player_rect = pygame.Rect(px, py, cube_size, cube_size)
        for rect, target, target_spawn in self.portals:
            if player_rect.colliderect(rect):
                return target, target_spawn
        return None, None


class HubScene(SceneBase):
    def __init__(self):
        # spawn in middle-left, e.g.
        super().__init__("hub", spawn=(100, 335))

    def load(self):
        self.cubes = []
        # flat grass, some decor
        cube_size = int(self.config.get('game.mines', 'block_size', fallback=50))
        portal_width = int(self.config.get('game.portals', 'portal_width', fallback=50))
        portal_height = int(self.config.get('game.portals', 'portal_height', fallback=700))

        for x in range(0, 1300, 50):
            item = Item(DIRT, 1, {"indestructable": True, "decoration": True})
            self.cubes.append(Block(x, 650, cube_size, cube_size, item))  # ground

        corridor_left = pygame.display.get_window_size()[0] - portal_width

        portal_mine_rect = pygame.Rect(corridor_left, 0, portal_width, portal_height)
        portal_shop_rect = pygame.Rect(0, 0, portal_width, portal_height)
        self.portals = [(portal_mine_rect, "mine", (50, 300)), (portal_shop_rect, "shop", (1100, 335))]


class MineScene(SceneBase):
    def __init__(self):
        super().__init__("mine", spawn=(50, 50))

    def load(self):
        self.cubes = []
        cube_size = int(self.config.get('game.mines', 'block_size', fallback=50))
        portal_width = int(self.config.get('game.portals', 'portal_width', fallback=50))
        portal_height = int(self.config.get('game.portals', 'portal_height', fallback=700))


        # build a small mine room with walls and floor
        for x in range(0, 1300, cube_size):
            item = Item(BEDROCK, 1, {"indestructable": True, "decoration": True})
            self.cubes.append(Block(x, 650, cube_size, cube_size, item))
            self.cubes.append(Block(x, 0, cube_size, cube_size, item))
            
        for y in range(0, 700, cube_size):
            item = Item(BEDROCK, 1, {"indestructable": True, "decoration": True})
            self.cubes.append(Block(1250, y, cube_size, cube_size, item))

        # Minable block cubes
        for x in range(cube_size + cube_size, 1300 - cube_size * 2, cube_size):
            for y in range(cube_size * 2, 600, cube_size):
                mat = random.choices(
                    population=[STONE, IRON, GOLD, DIAMOND],
                    weights=[10, 3, 1, 0.5],
                    k=1
                )[0]
                item = Item(mat, 1)
                self.cubes.append(Block(x, y, cube_size, cube_size, item))

        # portal back to hub at the far left
        back_rect = pygame.Rect(0, 0, portal_width, portal_height)
        self.portals = [(back_rect, "hub", (1100, 335))]

class ShopScene(SceneBase):
    def __init__(self):
        super().__init__("shop", spawn=(100, 335))

    def load(self):
        self.cubes = []

        cube_size = int(self.config.get('game.mines', 'block_size', fallback=50))
        portal_width = int(self.config.get('game.portals', 'portal_width', fallback=50))
        portal_height = int(self.config.get('game.portals', 'portal_height', fallback=700))

        for x in range(0, 1300, 50):
            item = Item(BEDROCK, 1, {"indestructable": True})
            self.cubes.append(Block(x, 650, cube_size, cube_size, item))

        corridor_left = pygame.display.get_window_size()[0] - portal_width
        corridor_rect = pygame.Rect(corridor_left, 0, portal_width, portal_height)  # "door" to the right
        self.portals = [(corridor_rect, "hub", (100, 335))]