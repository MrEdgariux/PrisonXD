class Rank:
    def __init__(self, name: str, price: int, color: tuple[int, int, int], requirements: dict[str, int] = {}):
        self.name = name
        self.price = price
        self.color = color
        self.requirements = requirements

class RankManager:
    def __init__(self):
        self.ranks: dict[str, Rank] = {}

    def register(self, rank: Rank):
        self.ranks[rank.name] = rank

    def get(self, name: str) -> Rank | None:
        return self.ranks.get(name)
    
    def all(self) -> list[Rank]:
        return list(self.ranks.values())