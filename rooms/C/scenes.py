import pygame, random
from mine import Block

from classes.items.materials import *
from classes.items.item import Item
from classes.shop import *
from ui.shop import ShopUI
from rooms.scenes import SceneBase

class HubScene(SceneBase):
    def __init__(self):
        # spawn in middle-left, e.g.
        super().__init__("c_hub", spawn=(100, 335))

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
        self.portals = [(portal_mine_rect, "c_mine", (50, 300)), (portal_shop_rect, "c_shop", (1100, 335))]

class MineScene(SceneBase):
    def __init__(self):
        super().__init__("c_mines", spawn=(50, 50))

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
        self.portals = [(back_rect, "c_hub", (1100, 335))]

class ShopScene(SceneBase):
    def __init__(self, shop_manager: ShopManager, shop_ui: ShopUI):
        super().__init__("c_shop", spawn=(100, 335))

        self.shop_manager: ShopManager = shop_manager
        self.shop_ui: ShopUI = shop_ui

        self.opened_shop: bool = False
        self.shop_active: Shop | None = None

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
        self.portals = [(corridor_rect, "c_hub", (100, 335))]

        self.shop = self.shop_manager.get("mine_sell_shop")  # ensure it's registered
        if not self.shop:
            raise ValueError("Shop 'mine_sell_shop' not found in ShopManager.")
        
    def update(self, player):
        next_scene, next_spawn = super().update(player)
        if next_scene:
            if self.shop_ui.visible:
                self.shop_ui.close()
            self.opened_shop = False
            self.shop_active = None
            return next_scene, next_spawn

        # If player is near the shop area (left side), open the shop UI
        px, py = player.position
        cube_size = int(self.config.get('game.mines', 'block_size', fallback=50))
        player_rect = pygame.Rect(px, py, cube_size, cube_size)

        shop_area = pygame.Rect(0, 0, 200, 700)
        if player_rect.colliderect(shop_area):
            if not self.opened_shop:
                if self.shop:
                    self.shop_ui.open(self.shop)
                    self.shop_active = self.shop
                self.opened_shop = True
        else:
            if self.opened_shop:
                self.shop_ui.close()
                self.shop_active = None
                self.opened_shop = False

        return None, None