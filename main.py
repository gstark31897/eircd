from threading import Thread
from socket import *
from select import select
import ssl


clients = []

def send_all(message, exclude):
    for client in clients:
        if client in exclude:
            continue
        client.send(message)


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

    def send(self, args):
        message = ""
        for i in range(0, len(args) - 1):
            message += "{} ".format(args[i])
        if len(args) > 1 and " " in args[-1]:
            message += ":{}\n".format(args[-1])
        else:
            message += "{}\n".format(args[-1])
        print(message)
        self.sock.send(message.encode("utf-8"))

    def send_all(self, message):
        send_all(message, self)

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
            self.buff += message
            while "\n" in self.buff:
                message, self.buff = self.buff.split('\n', 1)
                args = self._split_message(message)
                method = "_handle_{}".format(args[0]).lower()
                print(method)
                if not getattr(self, method)(*args[1:]):
                    return False
            return True
        except:
            return False

    def startup(self):
        self.send(["PING"])
        self.send(["NOTICE", "welcome to the eirc protocol"])

    def _handle_cap(self, *args):
        return True

    def _handle_nick(self, *args):
        print(args)
        return True

    def _handle_user(self, *args):
        print(args)
        return True

    def _handle_ping(self, *args):
        self.send(["PONG"])
        return True

    def _handle_pong(self, *args):
        return True

    def _handle_quit(self, *args):
        return False

    def _handle_privmsg(self, channel, message, *args):
        return True
        

server = socket(AF_INET, SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 6667))
server.listen(5)

while True:
    read, write, error = select(clients + [server], [], clients)
    for item in read:
        if item is server:
            client = Client(*server.accept())
            client.startup()
            clients.append(client)
            continue
        if not item.process():
            item.close()
            clients.remove(item)
            continue

