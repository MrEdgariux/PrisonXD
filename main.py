import pygame
import math
import random
import configparser

from mine import Block
from player.main import Player
from items.materials import Materials
from items.item import Item

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

config = configparser.ConfigParser()
settings = configparser.ConfigParser()

config.read('config.ini')
settings.read('settings.ini')

player = Player(screen.get_size())
cubes: list[Block] = []

for _ in range(10):
    x = random.randint(0, 1280)
    y = random.randint(0, 720)

    x = math.floor(x / 50) * 50
    y = math.floor(y / 50) * 50

    material = random.choice(Materials)
    item = Item(material, 1)
    cubes.append(Block(x, y, 50, 50, item))

is_mouse_down = False

while running:
    screen_res = pygame.display.get_surface().get_size()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            player.toggle_inventory()

    screen.fill((0, 155, 0))

    player_coordinates = player.position

    pygame.draw.rect(screen, (255, 0, 0), (player_coordinates[0], player_coordinates[1], 50, 50))

    for cube in cubes:
        screen.blit(cube.image, cube.rect)

    if player.inventory_open:
        inv_surf = player.get_inventory_surface()
        if inv_surf:
            screen.blit(inv_surf, (440, 210))

        pygame.display.flip()
        clock.tick(60)
        continue  # Skip movement and mining when inventory is open

    keys = pygame.key.get_pressed()
    player.moveHandler(keys, cubes)

    mouse_pressed = pygame.mouse.get_pressed()[0]

    if mouse_pressed and not is_mouse_down:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        mouse_x = math.floor(mouse_x / 50) * 50
        mouse_y = math.floor(mouse_y / 50) * 50

        player_coordinates = player.position
        
        # Get mining distance from config
        distance_x = int(config.get('game.mines', 'distance_x', fallback=25))
        distance_y = int(config.get('game.mines', 'distance_y', fallback=50))

        for cube in cubes:
            if cube.rect.collidepoint(mouse_x, mouse_y):
                if not (player_coordinates[0] in range(cube.rect.x - distance_x, cube.rect.x + cube.rect.width + distance_x) and player_coordinates[1] in range(cube.rect.y - distance_y, cube.rect.y + cube.rect.height + distance_y)):
                    print(f"Too far away to mine! Player: {player_coordinates}, Block: ({cube.rect.x}, {cube.rect.y})")
                    break
                print(f"Removing {cube.item.material.name} at: ({cube.rect.x}, {cube.rect.y})")
                success, items = player.inventory.add_item(cube.get_drops())
                cubes.remove(cube)
                break

    is_mouse_down = mouse_pressed

    pygame.display.flip()

    clock.tick(60)

pygame.quit()