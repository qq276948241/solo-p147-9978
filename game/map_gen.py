import random
from .entities import MapNode, NodeType


TOTAL_FLOORS = 5


def generate_map() -> list[list[MapNode]]:
    floors: list[list[MapNode]] = []
    
    for floor_idx in range(TOTAL_FLOORS + 1):
        if floor_idx == 0:
            nodes = [MapNode(NodeType.START, floor_idx, 0)]
        elif floor_idx == TOTAL_FLOORS:
            nodes = [MapNode(NodeType.BOSS, floor_idx, 0)]
        else:
            node_count = random.randint(4, 6)
            nodes = []
            for i in range(node_count):
                node_type = _random_node_type(floor_idx)
                nodes.append(MapNode(node_type, floor_idx, i))
        floors.append(nodes)
    
    _connect_floors(floors)
    return floors


def _random_node_type(floor: int) -> NodeType:
    weights = [
        (NodeType.BATTLE, 0.50),
        (NodeType.REST, 0.15),
        (NodeType.TREASURE, 0.15),
        (NodeType.SHOP, 0.20),
    ]
    if floor >= 3:
        weights = [
            (NodeType.BATTLE, 0.55),
            (NodeType.REST, 0.15),
            (NodeType.TREASURE, 0.10),
            (NodeType.SHOP, 0.20),
        ]
    
    r = random.random()
    cumulative = 0.0
    for node_type, weight in weights:
        cumulative += weight
        if r <= cumulative:
            return node_type
    return NodeType.BATTLE


def _connect_floors(floors: list[list[MapNode]]):
    for floor_idx in range(len(floors) - 1):
        current = floors[floor_idx]
        next_floor = floors[floor_idx + 1]
        
        if len(current) == 1:
            for node in next_floor:
                current[0].connections.append(node.index)
        else:
            for i, node in enumerate(current):
                if len(next_floor) == 1:
                    node.connections.append(0)
                else:
                    possible = []
                    if i > 0:
                        possible.append(max(0, i - 1))
                    possible.append(min(i, len(next_floor) - 1))
                    if i < len(next_floor) - 1:
                        possible.append(min(i + 1, len(next_floor) - 1))
                    possible = list(set(possible))
                    node.connections = possible
