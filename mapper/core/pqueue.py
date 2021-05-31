from typing import Any, Union, Dict, List


class PriorityQueue:

    def __init__(self):
        self.num_items = 0
        self.items: Dict[Union[int, float], List[Any]] = {}

    def queue(self, priority: Union[int, float], item: Any):
        if priority not in self.items.keys():
            self.items[priority] = []
        self.num_items += 1
        self.items[priority].append(item)

    def dequeue(self) -> Any:
        if self.num_items == 0:
            return None
        key = min(self.items.keys())
        self.num_items -= 1
        to_return = self.items[key].pop(0)
        if len(self.items[key]) == 0:
            self.items.pop(key)

        return to_return

    def empty(self) -> bool:
        return self.num_items == 0
