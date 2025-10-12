import pygame
import math
import random
import configparser

from mine import Block
from classes.player.main import Player
from classes.items.materials import Materials
from classes.items.item import Item
from classes.shop import ShopManager

from rooms.scene_manager import SceneManager

from ui.notifications import NotificationManager
from ui.debug import DebugOverlay
from ui.shop import ShopUI


from init import GameInit

pygame.init()
screen = pygame.display.set_mode((1300, 700))
clock = pygame.time.Clock()

notifier = NotificationManager(anchor="top-center")  # or "bottom-left"
debug = DebugOverlay(anchor="top-left", font=pygame.font.Font(None, 18))
shop_manager = ShopManager()
scene_mgr = SceneManager()

config = configparser.ConfigParser()
settings = configparser.ConfigParser()

config.read('config.ini')
settings.read('settings.ini')

player = Player(screen.get_size(), config, settings)
player.position = scene_mgr.current.spawn

GameInit(shop_manager)

debug.add_static("PrisonXD v0.1")
running = True
is_mouse_down = False

# Providers (each called every frame)
def perf_provider():
    return {
        "FPS": f"{clock.get_fps():.1f}",
        "Frame": f"{clock.get_time()} ms",
    }

def player_provider():
    px, py = player.position
    return {
        "Player": f"({px}, {py})",
    }

def scene_provider():
    try:
        cubes_count = len(scene_mgr.cubes())
        return {
            "Scene": scene_mgr.current.name,
            "Blocks": cubes_count,
        }
    except NameError:
        return {}
    
def mouse_hover_provider():
    mx, my = pygame.mouse.get_pos()
    mx = math.floor(mx / 50) * 50
    my = math.floor(my / 50) * 50
    return {
        "Mouse": f"({mx}, {my})",
    }

debug.add_provider(perf_provider)
debug.add_provider(player_provider)
debug.add_provider(scene_provider)
debug.add_provider(mouse_hover_provider)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            debug.toggle()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            player.toggle_inventory()

    screen.fill((0, 155, 0))

    pygame.draw.rect(screen, (255, 0, 0), (player.position[0], player.position[1], 50, 50))

    # SCENE UPDATE: check portals and switch if needed
    next_scene, next_spawn = scene_mgr.current.update(player)
    if next_scene:
        scene_mgr.switch(next_scene, player, next_spawn)

    if player.inventory_open:
        scene_mgr.current.draw(screen)
        inv_surf = player.get_inventory_surface()
        if inv_surf:
            screen.blit(inv_surf, (440, 210))

        pygame.display.flip()
        clock.tick(60)
        continue  # Skip movement and mining when inventory is open

    keys = pygame.key.get_pressed()
    player.moveHandler(keys, scene_mgr.cubes())

    mouse_pressed = pygame.mouse.get_pressed()[0]

    if mouse_pressed and not is_mouse_down:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        mouse_x = math.floor(mouse_x / 50) * 50
        mouse_y = math.floor(mouse_y / 50) * 50

        player_coordinates = player.position
        
        # Get mining distance from config
        distance_x = int(config.get('game.mines', 'distance_x', fallback=50))
        distance_y = int(config.get('game.mines', 'distance_y', fallback=50))

        for cube in scene_mgr.cubes().copy():
            if cube.rect.collidepoint(mouse_x, mouse_y):
                if not (player_coordinates[0] in range(cube.rect.x - distance_x, cube.rect.x + cube.rect.width + distance_x) and player_coordinates[1] in range(cube.rect.y - distance_y, cube.rect.y + cube.rect.height + distance_y)):
                    notifier.push("Too far away to mine!", "warning")
                    break

                if cube.item.metadata.get("indestructable", False):
                    notifier.push("Block is indestructable", "warning")
                    break
                print(f"Removing {cube.item.material.name} at: ({cube.rect.x}, {cube.rect.y})")
                success, items = player.inventory.add_item(cube.get_drops())
                scene_mgr.current.cubes.remove(cube)
                break

    is_mouse_down = mouse_pressed

    # draw scene
    scene_mgr.current.draw(screen)
    notifier.draw(screen)
    debug.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()