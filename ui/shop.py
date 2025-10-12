# ui/shop_ui.py
import pygame
from typing import Tuple, Optional, List
from classes.shop import Shop

class ShopUI:
    def __init__(self, font=None, width=520, height=360, margin=16):
        pygame.font.init()
        self.font = font or pygame.font.Font(None, 22)
        self.width, self.height = width, height
        self.margin = margin
        self.surface = pygame.Surface((width, height))
        self.visible = False
        self.shop: Optional[Shop] = None
        self.item_rows: List[Tuple[pygame.Rect, pygame.Rect, pygame.Rect, str]] = []
        # each row: (buy_rect, sell_rect, row_rect, item_id)

    def open(self, shop: Shop):
        self.shop = shop
        self.visible = True
        self._rebuild()

    def close(self):
        self.visible = False
        self.shop = None
        self.item_rows.clear()

    def toggle(self, shop: Shop):
        if self.visible and self.shop and self.shop.id == shop.id:
            self.close()
        else:
            self.open(shop)

    def _rebuild(self):
        assert self.shop
        self.surface.fill((30,30,30))
        title = self.font.render(f"{self.shop.display_name}", True, (255,255,255))
        self.surface.blit(title, (self.margin, self.margin))
        y = self.margin + 30
        self.item_rows = []
        row_h = 40
        for it in self.shop.items:
            # row background
            row_rect = pygame.Rect(self.margin, y, self.width - self.margin*2, row_h)
            pygame.draw.rect(self.surface, (45,45,45), row_rect)

            # item text
            name_s = self.font.render(f"{it.material.name}", True, (230,230,230))
            self.surface.blit(name_s, (self.margin + 6, y + 8))

            # Buy button (right side)
            buy_w = 80
            buy_rect = pygame.Rect(self.width - self.margin - buy_w, y + 6, buy_w, row_h - 12)
            pygame.draw.rect(self.surface, (0,120,0), buy_rect)
            buy_label = self.font.render(f"Buy {it.buy_price}", True, (255,255,255))
            self.surface.blit(buy_label, (buy_rect.x + 6, buy_rect.y + 8))

            # Sell button (between name and buy)
            sell_w = 80
            sell_rect = pygame.Rect(buy_rect.x - 10 - sell_w, y + 6, sell_w, row_h - 12)
            pygame.draw.rect(self.surface, (120,60,0), sell_rect)
            sell_label = self.font.render(f"Sell {it.sell_price}", True, (255,255,255))
            self.surface.blit(sell_label, (sell_rect.x + 6, sell_rect.y + 8))

            # store interactive rects in UI-local coords
            self.item_rows.append((buy_rect, sell_rect, row_rect, it.material.id))
            y += row_h + 8

    def draw(self, screen: pygame.Surface):
        if not self.visible or not self.shop:
            return
        # re-draw to reflect price/stock changes in case
        self._rebuild()
        sw, sh = screen.get_size()
        rect = self.surface.get_rect(center=(sw//2, sh//2))
        # dark background behind dialog
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0,0,0,120))
        screen.blit(overlay, (0,0))
        screen.blit(self.surface, rect.topleft)
        # we need to transform item rects into screen coords for event handling
        # mapping saved as attribute for convenience
        self._screen_rects = []
        for buy_rect, sell_rect, row_rect, item_id in self.item_rows:
            buy_screen = buy_rect.move(rect.left, rect.top)
            sell_screen = sell_rect.move(rect.left, rect.top)
            self._screen_rects.append((buy_screen, sell_screen, item_id))

    def handle_click(self, pos: Tuple[int,int]) -> Optional[Tuple[str,str,int]]:
        """Return (action, item_id, qty) where action in ('buy','sell'), qty default 1."""
        if not self.visible or not self.shop:
            return None
        for buy_r, sell_r, item_id in self._screen_rects:
            if buy_r.collidepoint(pos):
                return ("buy", item_id, 1)
            if sell_r.collidepoint(pos):
                return ("sell", item_id, 1)
        return None
