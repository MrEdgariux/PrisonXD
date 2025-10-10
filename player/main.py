from .inventory import PlayerInventory
from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_a, K_d, K_w, K_s

class Player:
    def __init__(self, res):
        self.inventory = PlayerInventory()
        self.position = (100, 100)
        self.res = res
        self.inventory_open = False
        self._inventory_surface = None  # cached surface

    def moveHandler(self, keys, obstacles=None):
        if keys[K_LEFT] or keys[K_a]:
            self.move(-5, 0, obstacles)
        if keys[K_RIGHT] or keys[K_d]:
            self.move(5, 0, obstacles)
        if keys[K_UP] or keys[K_w]:
            self.move(0, -5, obstacles)
        if keys[K_DOWN] or keys[K_s]:
            self.move(0, 5, obstacles)

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
        inv_container = pygame.Surface((400, 300))
        inv_container.fill((50, 50, 50))
        font = pygame.font.Font(None, 36)
        y_offset = 10
        itemai = self.inventory.get_items()
        for item in itemai:
            item_text = f"{item.material.name} x{item.quantity}"
            text_surf = font.render(item_text, True, (255, 255, 255))
            inv_container.blit(text_surf, (10, y_offset))
            y_offset += 40
        return inv_container

    def get_inventory_surface(self):
        return self._inventory_surface
        