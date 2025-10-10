from items.item import Item

class PlayerSlot:
    def __init__(self, index):
        self.index = index
        self.item: Item = None

    def is_empty(self):
        return self.item is None
    
    def is_full(self):
        if self.item:
            return self.item.quantity >= 64
        return False
    
    def add_item(self, item: Item):
        if self.is_empty():
            self.item = item
            return True, item
        elif self.item.material.id == item.material.id:
            available_space = 64 - self.item.quantity
            if available_space >= item.quantity:
                self.item.quantity += item.quantity
                return True, item
            elif available_space > 0:
                self.item.quantity += available_space
                item.quantity -= available_space
                return False, item
        return False, item
    
    def remove_item(self, item: Item):
        if self.item and self.item.material.id == item.material.id:
            if self.item.quantity >= item.quantity:
                self.item.quantity -= item.quantity
                if self.item.quantity == 0:
                    self.item = None
                return True, item
            else:
                removed_quantity = self.item.quantity
                self.item = None
                item.quantity -= removed_quantity
                return False, item
        return False, item

class PlayerInventory:
    def __init__(self):
        self.slots = [PlayerSlot(i) for i in range(10)]

    def add_item(self, item: Item):
        for slot in self.slots:
            if slot.is_empty() or (slot.item.material.id == item.material.id and not slot.is_full()):
                success, remaining_item = slot.add_item(item)
                if success:
                    return True, item
                else:
                    item = remaining_item
        return False, item
        
    def add_items(self, items: list[Item]):
        added_items = []
        for item in items:
            success, added_item = self.add_item(item)
            if success:
                added_items.append(added_item)
        return added_items

    def remove_item(self, item: Item):
        for slot in self.slots:
            if not slot.is_empty() and slot.item.material.id == item.material.id:
                success, remaining_item = slot.remove_item(item)
                if success:
                    return True, item
                else:
                    item = remaining_item
        return False, item

    def has_item(self, item: Item):
        total_quantity = 0
        for slot in self.slots:
            if not slot.is_empty() and slot.item.material.id == item.material.id:
                total_quantity += slot.item.quantity
                if total_quantity >= item.quantity:
                    return True
        return False
    
    def clear(self):
        items_cleared = []
        for slot in self.slots:
            if not slot.is_empty():
                items_cleared.append(slot.item)
            slot.item = None
        return items_cleared

    def get_item(self, slot_index:int):
        return self.slots[slot_index].item
    
    def get_items(self):
        items: list[Item] = []
        for slot in self.slots:
            if not slot.is_empty():
                items.append(slot.item)
        return items
    
    def __str__(self):
        return f"Inventory: {', '.join(self.items) if self.items else 'Empty'}"