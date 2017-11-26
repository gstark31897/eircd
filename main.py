from threading import Thread
from socket import *
from select import select
import ssl


class Client:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.buff = ""
        self.nick = ""

    def fileno(self):
        return self.sock.fileno()

    def close(self):
        self.sock.close()

    def send(self, message):
        self.sock.send(message.encode("utf-8"))

    def _split_message(self, message):
        args = []
        front, last = message, None
        if ":" in message:
            front, last = message.split(":", 1)
        args = front.split()
        if last is not None:
            args.append(last)
        return args

    def process(self):
        try:
            message = self.sock.recv(4096).decode("utf-8")
            if len(message) is 0:
                return False
        except:
            return False
        self.buff += message
        while "\n" in self.buff:
            message, self.buff = self.buff.split('\n', 1)
            print(self._split_message(message))
#            self.send("I got: " + message)
        return True

server = socket(AF_INET, SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 6667))
server.listen(5)

clients = []
while True:
    read, write, error = select(clients + [server], [], clients)
    for item in read:
        if item is server:
            client = Client(*server.accept())
            clients.append(client)
            continue
        if not item.process():
            item.close()
            clients.remove(item)
            continue

