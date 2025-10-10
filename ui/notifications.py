# ui/notifications.py
import pygame
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class Notification:
    text: str
    color: Tuple[int,int,int]
    bg: Tuple[int,int,int]
    duration: float = 2.5         # seconds visible before fade
    fade_time: float = 0.5        # seconds to fade out
    created_at: float = 0.0       # set by manager
    alpha: int = 255              # updated by manager

class NotificationManager:
    def __init__(self, font=None, max_width=380, margin=12, spacing=8, corner=12, anchor="top-right"):
        pygame.font.init()
        self.font = font or pygame.font.Font(None, 28)
        self.max_width = max_width
        self.margin = margin
        self.spacing = spacing
        self.corner = corner
        self.anchor = anchor
        self._items: List[Notification] = []

        # theme per level
        self.levels = {
            "info":    ((240,240,240), (40,40,40)),
            "success": ((230,255,230), (30,100,30)),
            "warning": ((255,240,230), (140,70,0)),
            "error":   ((255,228,228), (130,25,25)),
        }

    def push(self, text: str, level: str = "info", duration: float = None):
        fg, bg = self.levels.get(level, self.levels["info"])
        n = Notification(
            text=text,
            color=bg,       # text color
            bg=fg,          # bubble color
            duration=duration if duration is not None else 2.5,
        )
        n.created_at = pygame.time.get_ticks() / 1000.0
        self._items.append(n)

    def _wrap(self, text: str):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if self.font.size(test)[0] <= self.max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def update(self):
        # remove expired
        now = pygame.time.get_ticks() / 1000.0
        keep = []
        for n in self._items:
            t = now - n.created_at
            if t <= n.duration + n.fade_time:
                # compute alpha
                if t > n.duration:
                    k = 1.0 - (t - n.duration)/max(n.fade_time, 0.001)
                    n.alpha = max(0, min(255, int(255 * k)))
                else:
                    n.alpha = 255
                keep.append(n)
        self._items = keep

    def draw(self, screen: pygame.Surface):
        self.update()

        # pre-compute bubble surfaces for each notification
        bubbles = []
        for n in self._items:
            lines = self._wrap(n.text)
            pad = 10
            # width based on text strings
            w = min(self.max_width, max((self.font.size(line)[0] for line in lines), default=0)) + pad*2
            # height based on rendered line heights
            line_height = self.font.get_height()
            h = line_height * len(lines) + pad*2 + (len(lines)-1)*2

            bubble = pygame.Surface((w, h), pygame.SRCALPHA)
            # rounded rectangle background
            pygame.draw.rect(bubble, (*n.bg, n.alpha), bubble.get_rect(), border_radius=self.corner)

            # render and blit lines
            y = pad
            for line in lines:
                ln_surf = self.font.render(line, True, n.color)
                ln_surf.set_alpha(n.alpha)
                bubble.blit(ln_surf, (pad, y))
                y += line_height + 2

            bubbles.append(bubble)

        # stack bubbles near anchor
        screen_w, screen_h = screen.get_size()
        x = self.margin if not self.anchor.endswith("right") else screen_w - self.margin
        y = self.margin if not self.anchor.startswith("bottom") else screen_h - self.margin

        for bubble in reversed(bubbles):  # newest on top
            rect = bubble.get_rect()
            if self.anchor.endswith("right"):
                rect.topright = (x, y)
            else:
                rect.topleft = (x, y)

            screen.blit(bubble, rect)

            if self.anchor.startswith("bottom"):
                y -= rect.height + self.spacing
            else:
                y += rect.height + self.spacing
