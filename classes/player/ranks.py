class Rank:
    def __init__(self, id: str, display_name: str, price: int, color: tuple[int, int, int]):
        self.id = id
        self.display_name = display_name
        self.price = price
        self.color = color

class RankManager:
    def __init__(self):
        self.ranks: dict[str, Rank] = {}

    def register(self, rank: Rank):
        self.ranks[rank.id] = rank

    def get(self, id: str) -> Rank | None:
        return self.ranks.get(id)
    
    def all(self) -> list[Rank]:
        return list(self.ranks.values())