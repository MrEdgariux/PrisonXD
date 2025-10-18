from classes.player.inventory import PlayerInventory
from classes.player.stats import Stats
from classes.player.ranks import RankManager, Rank
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_a, K_d, K_w, K_s
from configparser import ConfigParser

import math

class Player:
    def __init__(self, res, config: ConfigParser, settings: ConfigParser, rank_manager: RankManager):

        self.rank_manager = rank_manager
        self.rank: Rank = rank_manager.get(config.get('game.player', 'default_rank', fallback="c"))

        self.config = config
        self.settings = settings

        self.walk_speed = config.getint('game.player', 'walk_speed', fallback=1) * 250

        self.slots = config.getint('game.player.inventory', 'slot_columns', fallback=9) * config.getint('game.player.inventory', 'slot_rows', fallback=4)
        self.inventory = PlayerInventory(self.slots, config.getint('game.player.inventory', 'slot_size', fallback=64))

        self.position = (100, 100)
        self.res = res

        self.inventory_open = False
        self._inventory_surface = None

        self.money = 0
        self.gems = 0

        self.stats = Stats()


    def moveHandler(self, keys, dt, obstacles=None):
        vx = float((keys[K_d] or keys[K_RIGHT]) - (keys[K_a] or keys[K_LEFT]))
        vy = float((keys[K_s] or keys[K_DOWN]) - (keys[K_w] or keys[K_UP]))

        # normalize to avoid faster diagonals
        length = math.hypot(vx, vy)
        if length > 0:
            vx /= length
            vy /= length
            self.move(vx * self.walk_speed * dt, vy * self.walk_speed * dt, obstacles)

    def move(self, dx, dy, obstacles=None):
        x, y = self.position
        new_position = (x + dx, y + dy)
        
        # Check collision with obstacles
        if obstacles:
            player_rect = (new_position[0], new_position[1], 50, 50)  # Assuming player is 50x50
            for obstacle in obstacles:
                if self.check_collision(player_rect, obstacle):
                    return  # Don't move if collision detected
        
        self.position = new_position

        # Boundary checks
        if self.position[0] < 0:
            self.position = (0, self.position[1])
        if self.position[0] > self.res[0] - 50:
            self.position = (self.res[0] - 50, self.position[1])
        if self.position[1] < 0:
            self.position = (self.position[0], 0)
        if self.position[1] > self.res[1] - 50:
            self.position = (self.position[0], self.res[1] - 50)
    
    def check_collision(self, rect1, obstacle):
        # rect format: (x, y, width, height)
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = obstacle.rect
        return (x1 < x2 + w2 and x1 + w1 > x2 and 
                y1 < y2 + h2 and y1 + h1 > y2)
    
    def toggle_inventory(self):
        self.inventory_open = not self.inventory_open
        if self.inventory_open:
            self._inventory_surface = self._build_inventory_surface()
        else:
            self._inventory_surface = None

    def _build_inventory_surface(self):
        import pygame
        # --- layout constants ---
        ROWS, COLS = self.config.getint('game.player.inventory', 'slot_rows', fallback=4), self.config.getint('game.player.inventory', 'slot_columns', fallback=9)
        SLOT = 56                 # slot outer size (px)
        GAP  = 6                  # gap between slots
        PAD  = 12                 # padding inside container
        LABEL_H = 28

        w = PAD*2 + COLS*SLOT + (COLS-1)*GAP
        h = PAD*3 + LABEL_H + ROWS*SLOT + (ROWS-1)*GAP

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # panel background
        pygame.draw.rect(surf, (35,35,35,235), surf.get_rect(), border_radius=12)

        # title
        font = pygame.font.Font(None, 28)
        title = font.render("Inventory", True, (255,255,255))
        surf.blit(title, (PAD, PAD))

        # grid origin
        grid_x = PAD
        grid_y = PAD*2 + LABEL_H

        # slot rects (ui-local) cached for hover
        self._inv_slot_rects = []   # list of pygame.Rect
        self._inv_slot_items = []   # parallel list of items (or None)

        # draw slots
        for r in range(ROWS):
            for c in range(COLS):
                idx = r*COLS + c
                x = grid_x + c*(SLOT+GAP)
                y = grid_y + r*(SLOT+GAP)
                rect = pygame.Rect(x, y, SLOT, SLOT)

                # slot background
                pygame.draw.rect(surf, (50,50,50), rect, border_radius=8)
                pygame.draw.rect(surf, (20,20,20), rect, width=2, border_radius=8)

                item = self.inventory.slots[idx].get_item()
                self._inv_slot_rects.append(rect)
                self._inv_slot_items.append(item)

                if item:
                    # inner block rect
                    inner = rect.inflate(-14, -14)
                    # color from material
                    color = getattr(item.material, "color", (200,200,200))
                    pygame.draw.rect(surf, color, inner, border_radius=6)
                    pygame.draw.rect(surf, (0,0,0), inner, width=2, border_radius=6)

                    # quantity (bottom-right)
                    q_font = pygame.font.Font(None, 24)
                    qty_s = q_font.render(str(item.quantity), True, (255,255,255))
                    surf.blit(qty_s, (rect.right - qty_s.get_width() - 6, rect.bottom - qty_s.get_height() - 4))

        return surf
    
    def draw_inventory(self, screen, topleft=(440, 210)):
        """
        Call this each frame when inventory is open.
        Renders the grid and shows a tooltip with item name on hover.
        """
        import pygame
        # (Re)build the inventory surface & slot rects
        inv_surface = self._build_inventory_surface()
        inv_rect = inv_surface.get_rect(topleft=topleft)

        # draw the container
        screen.blit(inv_surface, inv_rect.topleft)

        # hover detection: translate mouse to UI-local coords
        mx, my = pygame.mouse.get_pos()
        if not inv_rect.collidepoint((mx, my)):
            return  # mouse not over inventory

        local = (mx - inv_rect.left, my - inv_rect.top)

        # find hovered slot
        hovered_item = None
        hovered_rect = None
        for rect, item in zip(self._inv_slot_rects, self._inv_slot_items):
            if rect.collidepoint(local) and item:
                hovered_item = item
                hovered_rect = rect
                break

        if hovered_item:
            # build tooltip with item name
            name = getattr(hovered_item.material, "name", "Unknown")
            tip_font = pygame.font.Font(None, 24)
            text = tip_font.render(name, True, (255,255,255))
            pad = 6
            tip_w = text.get_width() + pad*2
            tip_h = text.get_height() + pad*2
            tip = pygame.Surface((tip_w, tip_h), pygame.SRCALPHA)
            pygame.draw.rect(tip, (0,0,0,200), tip.get_rect(), border_radius=6)
            tip.blit(text, (pad, pad))

            # place tooltip above the hovered slot (clamp to screen)
            # slot rect in screen coords:
            slot_screen = hovered_rect.move(inv_rect.left, inv_rect.top)
            tx = slot_screen.centerx - tip_w//2
            ty = slot_screen.top - tip_h - 8

            # clamp
            sw, sh = screen.get_size()
            tx = max(4, min(tx, sw - tip_w - 4))
            ty = max(4, ty)

            screen.blit(tip, (tx, ty))

    def rankup(self):
        next_rank = self.rank_manager.next(self.rank.id)
        if next_rank and self.money >= next_rank.price:
            self.money -= next_rank.price
            self.rank = next_rank
            return True, next_rank
        return False, None
    
    def add_money(self, amount):
        self.money += amount

    def add_gems(self, amount):
        self.gems += amount

    def take_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        return False
    
    def take_gems(self, amount):
        if self.gems >= amount:
            self.gems -= amount
            return True
        return False
        