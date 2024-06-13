import json
from typing import List, Optional

# Define the inner classes
class Limit:
    def __init__(self, blockType: str, upperLimit: int, lowerLimit: int):
        self.blockType = blockType
        self.upperLimit = upperLimit
        self.lowerLimit = lowerLimit

    def __repr__(self):
        return f"Limit(blockType={self.blockType}, upperLimit={self.upperLimit}, lowerLimit={self.lowerLimit})"

class Node:
    def __init__(self, name: str, qrID: int, ID: int, limits: List[Limit], range: int, colour: Optional[str] = None):
        self.name = name
        self.qrID = qrID
        self.ID = ID
        self.limits = limits
        self.range = range
        self.colour = colour

    def __repr__(self):
        return f"Node(name={self.name}, qrID={self.qrID}, limits={self.limits}, range={self.range}, colour={self.colour})"

class Ruleset:
    def __init__(self, name: str, nodes: List[Node]):
        self.name = name 
        self.nodes = nodes

    def __repr__(self):
        return f"Ruleset (name={self.name}, nodes={self.nodes})"

    def print(self):
        return "test"

# Function to parse the JSON data
    def parse_json(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        name = data["name"]
        nodes = []
        for node_data in data["nodes"]:
            limits = [
                Limit(limit["blockType"], limit["upperLimit"], limit["lowerLimit"])
                for limit in node_data.get("limits", [])
            ]
            node = Node(
                name=node_data["name"],
                qrID=node_data["qrID"],
                ID=node_data["ID"],
                limits=limits,
                range=node_data["range"],
                colour=node_data.get("colour")
            )
            nodes.append(node)
        return Ruleset(name, nodes)