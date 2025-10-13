from rooms.scenes import HubScene, MineScene, ShopScene

class SceneManager:
    def __init__(self, shop_manager, shop_ui):
        self.scenes = {
            "hub": HubScene(),
            "mine": MineScene(),
            "shop": ShopScene(shop_manager, shop_ui),
        }
        self.current: HubScene | MineScene = self.scenes["hub"]
        for s in self.scenes.values():
            s.load()

    def switch(self, name, player, spawn=None):
        self.current = self.scenes[name]
        # place player at the new spawn
        player.position = spawn if spawn else self.current.spawn

    def cubes(self):
        return self.current.cubes
