# ui/debug.py
import pygame
from typing import Dict, Callable, List, Tuple, Optional

class DebugOverlay:
    def __init__(self,
                 anchor: str = "top-left",
                 padding: int = 8,
                 bg=(0, 0, 0, 170),
                 text=(255, 255, 255),
                 font: Optional[pygame.font.Font] = None):
        """
        anchor: top-left | top-right | bottom-left | bottom-right | top-center | bottom-center
        """
        pygame.font.init()
        self.visible = False
        self.anchor = anchor
        self.padding = padding
        self.bg = bg
        self.text = text
        self.font = font or pygame.font.Font(None, 20)
        self._providers: List[Callable[[], Dict[str, str]]] = []
        self._static_lines: List[str] = []

    def toggle(self):
        self.visible = not self.visible

    def add_provider(self, fn: Callable[[], Dict[str, object]]):
        """Register a function returning a dict of debug key->value."""
        self._providers.append(fn)

    def add_static(self, line: str):
        """Optional: add a constant line (e.g., build/version)."""
        self._static_lines.append(line)

    def _anchor_rect(self, surf: pygame.Surface, screen: pygame.Surface) -> pygame.Rect:
        sw, sh = screen.get_size()
        r = surf.get_rect()
        a = self.anchor
        if a == "top-left":
            r.topleft = (self.padding, self.padding)
        elif a == "top-right":
            r.topright = (sw - self.padding, self.padding)
        elif a == "bottom-left":
            r.bottomleft = (self.padding, sh - self.padding)
        elif a == "bottom-right":
            r.bottomright = (sw - self.padding, sh - self.padding)
        elif a == "top-center":
            r.midtop = (sw // 2, self.padding)
        elif a == "bottom-center":
            r.midbottom = (sw // 2, sh - self.padding)
        else:
            r.topleft = (self.padding, self.padding)
        return r

    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return

        # Gather lines
        lines: List[str] = []
        lines.extend(self._static_lines)
        for prov in self._providers:
            try:
                d = prov() or {}
                for k, v in d.items():
                    lines.append(f"{k}: {v}")
            except Exception as e:
                lines.append(f"[provider error] {e}")

        # Render text to compute box size
        pad = self.padding
        lh = self.font.get_height()
        maxw = 0
        for ln in lines:
            w, _ = self.font.size(ln)
            maxw = max(maxw, w)
        w = maxw + pad * 2
        h = lh * len(lines) + pad * 2 + max(0, len(lines) - 1) * 2

        # Panel
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.bg, panel.get_rect(), border_radius=8)

        # Text
        y = pad
        for ln in lines:
            s = self.font.render(ln, True, self.text)
            panel.blit(s, (pad, y))
            y += lh + 2

        # Blit
        rect = self._anchor_rect(panel, screen)
        screen.blit(panel, rect)
