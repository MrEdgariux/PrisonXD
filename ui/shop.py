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
        
        # Scrolling properties
        self.scroll_offset = 0
        self.row_height = 40
        self.row_spacing = 8
        self.content_height = 0
        self.viewable_height = 0

    def open(self, shop: Shop):
        self.shop = shop
        self.visible = True
        self.scroll_offset = 0
        self._rebuild()

    def close(self):
        self.visible = False
        self.shop = None
        self.item_rows.clear()
        self.scroll_offset = 0

    def toggle(self, shop: Shop):
        if self.visible and self.shop and self.shop.id == shop.id:
            self.close()
        else:
            self.open(shop)

    def handle_scroll(self, direction: int):
        """Handle scroll wheel input. direction: -1 for up, 1 for down"""
        if not self.visible or not self.shop:
            return
            
        scroll_speed = 40
        self.scroll_offset += direction * scroll_speed
        
        # Clamp scroll offset
        max_scroll = max(0, self.content_height - self.viewable_height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def _rebuild(self):
        assert self.shop
        self.surface.fill((30,30,30))
        title = self.font.render(f"{self.shop.display_name}", True, (255,255,255))
        self.surface.blit(title, (self.margin, self.margin))
        
        # Calculate viewable area
        title_height = 30
        self.viewable_height = self.height - self.margin * 2 - title_height
        
        # Count visible items and calculate content height
        visible_items = [it for it in self.shop.items if it.buy_price > 0 or it.sell_price > 0]
        self.content_height = len(visible_items) * (self.row_height + self.row_spacing)
        
        # Create a surface for scrollable content
        content_surface = pygame.Surface((self.width - self.margin * 2, max(self.content_height, self.viewable_height)))
        content_surface.fill((30,30,30))
        
        y = 0
        self.item_rows = []
        
        for it in self.shop.items:
            if it.buy_price <= 0 and it.sell_price <= 0:
                continue
                
            # row background
            row_rect = pygame.Rect(0, y, self.width - self.margin*2, self.row_height)
            pygame.draw.rect(content_surface, (45,45,45), row_rect)

            # item text
            name_s = self.font.render(f"{it.material.name}", True, (230,230,230))
            content_surface.blit(name_s, (6, y + 8))

            buy_rect = None
            sell_rect = None

            buy_w = 80
            buy_rect_candidate = pygame.Rect(self.width - self.margin*2 - buy_w, y + 6, buy_w, self.row_height - 12)

            sell_w = 80
            sell_rect_candidate = pygame.Rect(buy_rect_candidate.x - 10 - sell_w, y + 6, sell_w, self.row_height - 12)

            if it.buy_price > 0:
                buy_rect = buy_rect_candidate
                pygame.draw.rect(content_surface, (0,120,0), buy_rect)
                buy_label = self.font.render(f"Buy {it.buy_price}", True, (255,255,255))
                content_surface.blit(buy_label, (buy_rect.x + 6, buy_rect.y + 8))

            if it.sell_price > 0:
                sell_rect = sell_rect_candidate
                pygame.draw.rect(content_surface, (120,60,0), sell_rect)
                sell_label = self.font.render(f"Sell {it.sell_price}", True, (255,255,255))
                content_surface.blit(sell_label, (sell_rect.x + 6, sell_rect.y + 8))

            # Adjust rects for scrolling
            if buy_rect:
                buy_rect = buy_rect.move(self.margin, self.margin + title_height - self.scroll_offset)
            if sell_rect:
                sell_rect = sell_rect.move(self.margin, self.margin + title_height - self.scroll_offset)
            
            row_rect = row_rect.move(self.margin, self.margin + title_height - self.scroll_offset)
            
            # store rects (may be None) and item id
            self.item_rows.append((buy_rect, sell_rect, row_rect, it.material.id))
            y += self.row_height + self.row_spacing

        # Blit the scrollable content to main surface
        content_rect = pygame.Rect(0, self.scroll_offset, self.width - self.margin*2, self.viewable_height)
        self.surface.blit(content_surface, (self.margin, self.margin + title_height), content_rect)
        
        # Draw scrollbar if needed
        if self.content_height > self.viewable_height:
            self._draw_scrollbar()

    def _draw_scrollbar(self):
        """Draw a scrollbar on the right side"""
        scrollbar_width = 8
        scrollbar_x = self.width - self.margin - scrollbar_width
        scrollbar_y = self.margin + 30
        scrollbar_height = self.viewable_height
        
        # Background
        pygame.draw.rect(self.surface, (60,60,60), 
                        (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
        
        # Thumb
        if self.content_height > 0:
            thumb_height = max(20, int(scrollbar_height * self.viewable_height / self.content_height))
            thumb_y = scrollbar_y + int(self.scroll_offset * (scrollbar_height - thumb_height) / max(1, self.content_height - self.viewable_height))
            
            pygame.draw.rect(self.surface, (120,120,120), 
                            (scrollbar_x, thumb_y, scrollbar_width, thumb_height))

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

        # map only non-None rects into screen coords for event handling
        self._screen_rects = []  # list of tuples (buy_screen_or_None, sell_screen_or_None, item_id)
        for buy_rect, sell_rect, row_rect, item_id in self.item_rows:
            # Only include rects that are visible in the viewport
            viewport_top = self.margin + 30
            viewport_bottom = viewport_top + self.viewable_height
            
            if row_rect and row_rect.bottom >= viewport_top and row_rect.top <= viewport_bottom:
                buy_screen = buy_rect.move(rect.left, rect.top) if buy_rect else None
                sell_screen = sell_rect.move(rect.left, rect.top) if sell_rect else None
                self._screen_rects.append((buy_screen, sell_screen, item_id))

    def handle_click(self, pos: Tuple[int,int]) -> Optional[Tuple[str,str,int]]:
        """Return (action, item_id, qty) where action in ('buy','sell'), qty default 1."""
        if not self.visible or not self.shop:
            return None
        for buy_r, sell_r, item_id in self._screen_rects:
            if buy_r and buy_r.collidepoint(pos):
                return ("buy", item_id, 1)
            if sell_r and sell_r.collidepoint(pos):
                return ("sell", item_id, 1)
        return None
