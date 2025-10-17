import pygame, math, random, configparser
from mine import Block

from classes.items.materials import *
from classes.items.item import Item
from classes.shop import *
from classes.player.main import Player
from ui.shop import ShopUI

import pygame
import textwrap

def draw_text_in_rect(
    surface: pygame.Surface,
    text: str,
    rect: pygame.Rect,
    *,
    font_name="robotomono",
    max_font_size=24,
    min_font_size=10,
    color=(0, 0, 255),
    padding=6,
    ellipsis=True,
    line_spacing=1.1,
    center=True
):
    """Draw text inside rect, wrapping and shrinking to fit. Returns final font size used."""
    inner_w = max(0, rect.width - 2*padding)
    inner_h = max(0, rect.height - 2*padding)

    if inner_w <= 0 or inner_h <= 0:
        return None

    def wrap_lines(font: pygame.font.Font, txt: str) -> list[str]:
        # Wrap by measuring candidate lines (word-based)
        words = txt.split()
        if not words:
            return []
        lines, cur = [], words[0]
        for w in words[1:]:
            test = cur + " " + w
            if font.size(test)[0] <= inner_w:
                cur = test
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        return lines

    fs = max_font_size
    chosen_lines = []
    chosen_font = None

    while fs >= min_font_size:
        f = pygame.font.SysFont(font_name, fs)
        lines = wrap_lines(f, text)

        # Measure total height
        line_h = f.get_linesize()
        total_h = int(line_h * line_spacing * len(lines))

        if total_h <= inner_h:
            chosen_lines = lines
            chosen_font = f
            break
        fs -= 1

    # If still too tall, we’ll truncate with ellipsis using the min size
    if chosen_font is None:
        chosen_font = pygame.font.SysFont(font_name, min_font_size)
        lines = wrap_lines(chosen_font, text)

        # Remove lines until it fits
        line_h = chosen_font.get_linesize()
        while lines and int(line_h * line_spacing * len(lines)) > inner_h:
            lines.pop()

        if lines and ellipsis:
            # Try to add ellipsis to the last line without exceeding width
            last = lines[-1]
            while last and chosen_font.size(last + "…")[0] > inner_w:
                last = last[:-1]
            lines[-1] = (last + "…") if last else "…"

        chosen_lines = lines

    # Render
    # Optional: draw a subtle background so text is readable
    # pygame.draw.rect(surface, (0, 0, 0, 80), rect)  # if using per-surface alpha

    # Clip to ensure no overflow ever shows
    prev_clip = surface.get_clip()
    surface.set_clip(rect)

    y = rect.y + padding
    # Vertical centering
    if center and chosen_lines:
        line_h = chosen_font.get_linesize()
        block_h = int(line_h * line_spacing * len(chosen_lines))
        y = rect.y + (rect.height - block_h) // 2

    for line in chosen_lines:
        img = chosen_font.render(line, True, color)
        if center:
            x = rect.x + (rect.width - img.get_width()) // 2
        else:
            x = rect.x + padding
        surface.blit(img, (x, y))
        y += int(chosen_font.get_linesize() * line_spacing)

    surface.set_clip(prev_clip)
    return chosen_font.get_height() if chosen_lines else None


class SceneBase:
    def __init__(self, name, spawn=(100,100), min_rank_id: str | None = None):
        self.name = name
        self.spawn = spawn
        self.min_rank_id = min_rank_id # if set, player must have this rank or higher to enter
        self.config = configparser.ConfigParser()
        self.settings = configparser.ConfigParser()
        self.cubes: list[Block] = []
        self.portals = []  # list of (rect, target_scene_name, target_spawn)

        self.config.read('config.ini')
        self.settings.read('settings.ini')

    def load(self):
        """(Re)create blocks/portals for this scene."""
        pass

    def draw(self, screen, player: Player):
        for cube in self.cubes:
            screen.blit(cube.image, cube.rect)
        # Show portals and their titles
        for p in self.portals:
            r = p[0]
            name = p[1]
            pygame.draw.rect(screen, (0, 0, 255), r, 2)
            draw_text_in_rect(
                screen,
                name,
                r,
                font_name="robotomono",
                max_font_size=18,
                min_font_size=8,
                color=(0, 0, 255),
                padding=6,
                ellipsis=True,
                line_spacing=1.1,
                center=True
            )

        # A title at the top
        font = pygame.font.SysFont("robotomono", 36)
        text = font.render(self.name.upper().replace('_', ' '), True, (255, 255, 255))
        screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 10))

        # Balance at the bottom right
        font = pygame.font.SysFont("robotomono", 24)
        text = font.render(f"Balance: ${player.money}", True, (255, 255, 0))
        screen.blit(text, (screen.get_width() - text.get_width() - 10, screen.get_height() - text.get_height() - 10))

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
        super().__init__("hub", spawn=(100, 335), min_rank_id=None)

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

        # Create 3 mine portals on the right side, dividing the height by 3
        portal_height_per_mine = portal_height // 3
        portal_c_mine_rect = pygame.Rect(corridor_left, 0, portal_width, portal_height_per_mine)
        portal_b_mine_rect = pygame.Rect(corridor_left, portal_height_per_mine, portal_width, portal_height_per_mine)
        portal_a_mine_rect = pygame.Rect(corridor_left, portal_height_per_mine * 2, portal_width, portal_height_per_mine)
        
        self.portals = [
            (portal_c_mine_rect, "c_hub", (250, 300)),
            (portal_b_mine_rect, "b_hub", (250, 300)),
            (portal_a_mine_rect, "a_hub", (250, 300)),
            # (portal_shop_rect, "shop", (1100, 335))
        ]