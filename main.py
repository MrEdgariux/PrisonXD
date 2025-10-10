import pygame
import math
import random
import configparser

from mine import Block
from player.main import Player
from items.materials import Materials
from items.item import Item

from rooms.scene_manager import SceneManager

pygame.init()
screen = pygame.display.set_mode((1300, 700))
clock = pygame.time.Clock()
running = True

config = configparser.ConfigParser()
settings = configparser.ConfigParser()

config.read('config.ini')
settings.read('settings.ini')

player = Player(screen.get_size(), config, settings)
cubes: list[Block] = []

scene_mgr = SceneManager()
player.position = scene_mgr.current.spawn

is_mouse_down = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
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

        print(f"Mouse clicked at: ({mouse_x}, {mouse_y})")

        player_coordinates = player.position
        
        # Get mining distance from config
        distance_x = int(config.get('game.mines', 'distance_x', fallback=50))
        distance_y = int(config.get('game.mines', 'distance_y', fallback=50))

        for cube in scene_mgr.cubes().copy():
            if cube.rect.collidepoint(mouse_x, mouse_y):
                if not (player_coordinates[0] in range(cube.rect.x - distance_x, cube.rect.x + cube.rect.width + distance_x) and player_coordinates[1] in range(cube.rect.y - distance_y, cube.rect.y + cube.rect.height + distance_y)):
                    print(f"Too far away to mine! Player: {player_coordinates}, Block: ({cube.rect.x}, {cube.rect.y})")
                    break

                if cube.item.metadata.get("indestructable", False):
                    print(f"Block at ({cube.rect.x}, {cube.rect.y}) is indestructable.")
                    break
                print(f"Removing {cube.item.material.name} at: ({cube.rect.x}, {cube.rect.y})")
                success, items = player.inventory.add_item(cube.get_drops())
                scene_mgr.current.cubes.remove(cube)
                break

    is_mouse_down = mouse_pressed

    # draw scene
    scene_mgr.current.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()