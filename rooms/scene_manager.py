from rooms.scenes import HubScene, MineScene, ShopScene

class SceneManager:
    def __init__(self):
        self.scenes = {
            "hub": HubScene(),
            "mine": MineScene(),
            "shop": ShopScene(),
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
