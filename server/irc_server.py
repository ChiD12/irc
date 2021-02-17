import sys

# sys.path.insert(1, '../../client')

import socket
import threading
from _thread import *
import patterns

sockets = {}
lock = threading.Lock()

class clientManager(patterns.Subscriber):
    def __init__(self):
        self.clients = dict()

    def addClient(self, connection, address):
        self.clients[address[1]] = client(connection, address)

    def removeClient(self,id):
        del self.clients[id]

    def notify(self, addr, msg):
        lock.acquire()
        for key in self.clients:
            self.clients[key].update(msg)
        lock.release() 


class client():
    def __init__(self, conn, addr):
        self.name = ""
        self.conn = conn
        self.id = addr[1]
        self.addr = addr[0]

    def update(self, msg):
        self.conn.send(msg)

def clientRun(manager, conn, addr):
    with conn:
        print('Connected by', addr[1], conn)
        manager.addClient(conn, addr)
        # sockets[addr[1]] = conn
        while True:
            data = conn.recv(1024)
            if not data: break
            print(data)
            decoded = data.decode('utf-8')
            if decoded == "close":
                manager.removeClient(addr[1])
                break
            # conn.sendall(data)
            manager.notify(addr[1], data)


def main(args):
    manager = clientManager()
    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = 50007
              # Arbitrary non-privileged port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        # s.settimeout(0.5)
        # s.setblocking(0)
        while True:
            try:
                conn, addr = s.accept()
                # threading.Thread(target=clientRun, args=(manager,conn, addr))
                start_new_thread(clientRun, (manager,conn, addr))
            except KeyboardInterrupt:
                print('kbinter')
                break

    print(manager.clients)



if __name__ == "__main__":
    # Parse your command line arguments here
    args = None
    main(args)