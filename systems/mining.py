# systems/mining.py
import pygame
from typing import Optional

from classes.player.main import Player
from rooms.scene_manager import SceneManager

class MiningSystem:
    def __init__(self, config, notifier):
        self.config = config
        self.notifier = notifier
        self._is_mouse_down = False
        self._last_mine_time = 0
        self._cooldown_ms = self.config.getint('game.mines', 'click_cooldown_ms', fallback=120)

    # Optional: call this every frame if you prefer polling-style
    def update(self, player, scene_mgr):
        pass

    # Event-style mining (recommended): call from main event loop
    def handle_event(self, event, player: Player, scene_mgr: SceneManager, *, ignore_when=lambda: False):
        if ignore_when() or not scene_mgr.current:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._is_mouse_down = True
            return self._try_mine_now(player, scene_mgr)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._is_mouse_down = False

        return False

    # ---- internals ----

    def _try_mine_now(self, player: Player, scene_mgr: SceneManager) -> bool:
        # cooldown
        now = pygame.time.get_ticks()
        if now - self._last_mine_time < self._cooldown_ms:
            return False
        self._last_mine_time = now

        # snap mouse to grid
        block_size = self.config.getint('game.mines', 'block_size', fallback=50)
        mx, my = pygame.mouse.get_pos()
        gx = (mx // block_size) * block_size
        gy = (my // block_size) * block_size

        # reach check
        reach_x = self.config.getint('game.mines', 'distance_x', fallback=50)
        reach_y = self.config.getint('game.mines', 'distance_y', fallback=50)

        # search target block
        cubes = scene_mgr.cubes().copy()
        for cube in cubes:
            if cube.rect.collidepoint(gx, gy):
                px, py = player.position
                in_reach = (
                    int(px) in range(cube.rect.left - reach_x, cube.rect.right + reach_x + 1) and
                    int(py) in range(cube.rect.top  - reach_y, cube.rect.bottom + reach_y + 1)
                )
                print(f"Mining attempt at ({gx}, {gy}), player at ({px}, {py}), in_reach={in_reach}")
                if not in_reach:
                    self.notifier.push("Too far away to mine!", "warning")
                    return True

                # indestructible?
                if getattr(cube.item, "metadata", {}).get("indestructable", False):
                    self.notifier.push("Block is indestructable", "warning")
                    return True

                # collect drops
                drops = cube.get_drops()
                ok, leftover = player.inventory.add_item(drops)

                # remove block from scene
                try:
                    scene_mgr.current.cubes.remove(cube)
                except ValueError:
                    pass

                # feedback
                try:
                    # handle either Item or list[Item]
                    if isinstance(drops, list):
                        name = drops[0].material.name
                        qty  = sum(d.quantity for d in drops)
                    else:
                        name = drops.material.name
                        qty  = drops.quantity
                    self.notifier.push(f"Picked up {name} x{qty}", "success")
                    player.stats.blocks_mined += qty
                except Exception:
                    pass

                if not ok:
                    self.notifier.push("Inventory full (some items not added)", "warning")

                return True

        return False
