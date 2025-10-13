from rooms.scenes import HubScene, MineScene, ShopScene
from rooms.C.scenes import HubScene as CHubScene, MineScene as CMineScene, ShopScene as CShopScene

class SceneManager:
    def __init__(self, shop_manager, shop_ui):
        self.scenes = {
            "hub": HubScene(),
            "mine": MineScene(),
            "shop": ShopScene(shop_manager, shop_ui),

            "c_hub": CHubScene(),
            "c_mine": CMineScene(),
            "c_shop": CShopScene(shop_manager, shop_ui),
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
