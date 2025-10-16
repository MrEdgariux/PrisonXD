import pygame
import math
import random
import configparser

from mine import Block
from classes.player.main import Player
from classes.items.materials import Materials
from classes.items.item import Item
from classes.shop import ShopManager
from classes.player.ranks import RankManager, Rank
from classes.chat.commands.command_handler import CommandRegistry, CommandContext

from rooms.scene_manager import SceneManager
from rooms.scenes import ShopScene

from ui.notifications import NotificationManager
from ui.debug import DebugOverlay
from ui.shop import ShopUI
from ui.chat import ChatUI

from init import GameInit

from helper import *

pygame.init()
screen = pygame.display.set_mode((1300, 700))
clock = pygame.time.Clock()

notifier = NotificationManager(anchor="top-center")  # or "bottom-left"
debug = DebugOverlay(anchor="top-left", font=pygame.font.Font(None, 18))
chat = ChatUI(10, 400, 400, 290)
cmds = CommandRegistry()
shop_manager = ShopManager()
shop_ui = ShopUI()
rank_manager = RankManager()
GameInit(shop_manager, rank_manager, cmds)
scene_mgr = SceneManager(shop_manager, shop_ui)

config = configparser.ConfigParser()
settings = configparser.ConfigParser()

config.read('config.ini')
settings.read('settings.ini')

player = Player(screen.get_size(), config, settings, rank_manager)
player.position = scene_mgr.current.spawn

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

def rank_provider():
    if player.rank:
        return {
            "Rank": f"{player.rank.display_name} (${player.rank.price})",
        }
    else:
        return {
            "Rank": "None",
        }
    
def ranks_provider():
    ranks = rank_manager.all()
    if ranks:
        return {
            "Ranks": " > ".join([rank.display_name for rank in ranks])
        }
    else:
        return {
            "Ranks": "None"
        }

debug.add_provider(perf_provider)
debug.add_provider(player_provider)
debug.add_provider(scene_provider)
debug.add_provider(mouse_hover_provider)
debug.add_provider(rank_provider)
debug.add_provider(ranks_provider)

# -- HELPER FUNCTIONS --

def make_ctx():
    return CommandContext(
        player=player,
        scene_mgr=scene_mgr,
        notifier=notifier,
        chat=chat,
        shop_ui=shop_ui,
        shop_mgr=shop_manager,
        config=config,
        debug=debug,
    )

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not chat.is_chat_open):
            running = False
        if chat.is_chat_open:
            chat_message = chat.handle_event(event)
            if chat_message:
                if chat_message.startswith("/"):
                    cmds.run(make_ctx(), chat_message[1:])
                else:
                    chat.add_message("Player", chat_message, (255, 255, 255))
                print(f"Chat message: {chat_message}")
            continue
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            debug.toggle()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            player.toggle_inventory()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # If shop UI is open, handle clicks there first
            if shop_ui.visible:
                action = shop_ui.handle_click((mx, my))
                if action and scene_mgr.current and isinstance(scene_mgr.current, ShopScene):
                    process_shop_action(player, scene_mgr.current.shop, action, notifier)
                continue
        elif event.type == pygame.MOUSEWHEEL:
            if shop_ui.visible:
                shop_ui.handle_scroll(-event.y)  # Invert to match typical scroll direction
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            chat.toggle_chat()

    screen.fill((0, 155, 0))

    pygame.draw.rect(screen, (255, 0, 0), (player.position[0], player.position[1], 50, 50))

    # SCENE UPDATE: check portals and switch if needed
    next_scene, next_spawn = scene_mgr.current.update(player)
    if next_scene:
        scene_mgr.switch(next_scene, player, next_spawn)

    if player.inventory_open:
        scene_mgr.current.draw(screen, player)
        inv_surf = player.get_inventory_surface()
        if inv_surf:
            screen.blit(inv_surf, (440, 210))

        pygame.display.flip()
        clock.tick(60)
        continue  # Skip movement and mining when inventory is open

    keys = pygame.key.get_pressed()
    if not chat.is_chat_open:
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
    scene_mgr.current.draw(screen, player)
    notifier.draw(screen)
    debug.draw(screen)
    shop_ui.draw(screen)
    chat.update(clock.get_time())
    chat.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()