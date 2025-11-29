class PBFT:
    def __init__(self, nodes):
        self.nodes = nodes
        self.requests = []

    def request(self, data):
        self.requests.append(data)
        self.broadcast(data)

    def broadcast(self, data):
        for node in self.nodes:
            node.receive(data)

    def receive(self, data):
        pass
