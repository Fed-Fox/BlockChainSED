import hashlib
import time
import json

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

class Blockchain:
    def __init__(self):
        self.chain = []
        with open("database/filesbc.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for block in data["blockchains"]:
                self.chain.append(Block(len(self.chain), block["previous_hash"], block["timestamp"], block["data"], block["hash"]))

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), previous_block.hash, time.time(), data, self.calculate_hash(previous_block.hash, data))
        self.chain.append(new_block)

        with open("database/filesbc.json", "r", encoding="utf-8") as f:
            filedata = json.load(f)

            datanew = {
                "index": len(self.chain),
                "previous_hash": previous_block.hash,
                "timestamp": time.time(),
                "data": data, 
                "hash": self.calculate_hash(previous_block.hash, data)
            }

            filedata["blockchains"].append(datanew)

            with open('database/filesbc.json', 'w', encoding='utf8') as f:
                json.dump(filedata, f, ensure_ascii=True, indent=4)
            

    def calculate_hash(self, previous_hash, data):
        return hashlib.sha256(f"{previous_hash}{data}".encode()).hexdigest()

    def receive(self, data):
        self.add_block(data)
