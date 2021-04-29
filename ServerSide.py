from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint

from fun_on_a_bun_part_2 import ServerCollector

class TurnOffWhenNoConnections():

    def __init__(self, final_function):
        self.final_function = final_function
        self._result = 0

    def __set__(self, obj, num):
        self._result = num
        if self._result == 0:
            self.final_function()

    def __get__(self, obj, attr):
        return self._result

class ServerFactory(Factory):

    active_connections = TurnOffWhenNoConnections(lambda: reactor.stop())
    def buildProtocol(self, addr):
        server = Server(self)
        server.add_broadcast_machine(ServerCollector(server, lambda x, y: x + y, 2))
        return server


class Server(LineReceiver):

    def __init__(self, factory, *args, **kwargs):
        self.factory = factory
        self.machines = []
        super().__init__(*args, **kwargs)

    def add_broadcast_machine(self, machine):
        self.machines.append(machine)

    def connectionMade(self):
        self.factory.active_connections += 1
        self.transport.write(b"Welcome to the server!\n\r")

    def connectionLost(self, reason):
        self.factory.active_connections -= 1
        print("client disconnected: {}".format(reason))

    def lineReceived(self, line):
        for machine in self.machines:
            machine.send_message(line)

if __name__ == '__main__':
    port = 8123
    endpoint = TCP4ServerEndpoint(reactor, port)
    endpoint.listen(ServerFactory())
    reactor.run()
