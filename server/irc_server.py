import sys

# sys.path.insert(1, '../../client')

import socket
import threading
from _thread import *
import logging

logging.basicConfig(filename='server.log', level=logging.DEBUG)
logger = logging.getLogger()


sockets = {}
lock = threading.Lock()

servername = "Awesomeserver"

class clientManager():
    def __init__(self):
        self.clients = dict()
        print("init")

    def addClient(self, nick, user, connection, address):
        self.clients[address[1]] = client(nick, user, connection, address)
        return self.clients[address[1]]

    def removeClient(self,id):
        del self.clients[id]

    def notify(self, addr, msg, sentFrom, channel):
        for key in self.clients:
            self.clients[key].update(msg, sentFrom, channel)

    def nickExists(self, nick):
        if not self.clients:  #if clients is empty
            return False
        for key in self.clients:
            if self.clients[key].nick == nick:
                return True
        return False


class client():
    def __init__(self, nick, user, conn, addr):
        self.nick = nick
        self.user = user
        self.conn = conn
        self.id = addr[1]
        self.addr = addr[0]
        self.channels = ["#global"]

    def update(self, msg, sentFrom, channel ):
        if sentFrom != self.nick and channel in self.channels:
            msg = str.encode("{}".format(msg)) #TODO irc stuff
            self.conn.send(msg)


def clientRun(manager, conn, addr):

    def checkLength(msg):
        return len(msg)>512

    NICK = str()
    USER = str()

    with conn:
        print('Connected by', addr[1], conn)
        #loop until untaken user or quit
        user = ""
        currentClient = ""
        while True:
            user = conn.recv(1024).decode('utf-8')
            print("REQUEST: {}".format(user))
            logger.info("REQUEST: {}".format(user))
            
            if checkLength(user):   #check if msg is less than 512 characters
                continue

            user = user.split(' ')
            

            if user[0] == "NICK":
                if not manager.nickExists(user[1]):
                    NICK = user[1]
                    print("nick is {}".format(user[1]) )
                else:
                    resp = str.encode("{} 433 * {} :Nickname is already in use \r\n".format(servername, user[1]))
                    conn.sendall(resp) 
                    print("RESPONSE: {}".format(resp))
                    logger.info("RESPONSE: {}".format(resp))
                    

            if user[0] == "USER" and NICK != str():
                print("user is {}".format(user[1]) )
                USER = user[1]

            elif user == "QUIT":  #TODO irc stuff
                conn.close()
                break

            if NICK != str() and USER != str():
                    #send message to everyone saying user joined
                    print("in here")
                    currentClient = manager.addClient(NICK, USER, conn, addr)
                    resp = str.encode(":{} 001 {} :Welcome to 445 IRC {}!{}@{} \r\n".format(servername, NICK, NICK, USER, currentClient.addr))
                    conn.sendall(resp)
                    print("RESPONSE: {}".format(resp))
                    logger.info("RESPONSE: {}".format(resp))

                    #apparently this is a hexchat feature and not irc
                    notifyMsg = "JOIN {}!{}@{} has joined \r\n".format(NICK, USER, addr[0])
                    manager.notify(addr[1], notifyMsg, "Server", "#global")
                    print("RESPONSE ALL : {}".format(notifyMsg))
                    logger.info("RESPONSE ALL : {}".format(notifyMsg))
                    break
            
        # sockets[addr[1]] = conn
        #loop for messages
        while True:
            data = conn.recv(1024)
            if not data: break
            
            msg = data.decode('utf-8')  #check if msg is less than 512 characters
            print("REQUEST: {}".format(msg))
            logger.info("REQUEST: {}".format(msg))
            if checkLength(msg): 
                conn.sendall(b"user joined")
                continue
            if msg == "QUIT":
                manager.removeClient(addr[1])
                for channel in currentClient.channels:  #tell every channel that user has left
                    notifyMsg = "QUIT {}!{}@{} has left \r\n".format(NICK, USER, addr[0])
                    manager.notify(addr[1], notifyMsg, "Server", channel)
                    print("RESPONSE ALL : {}".format(notifyMsg))
                    logger.info("RESPONSE ALL : {}".format(notifyMsg))
                conn.close()
                break
            # conn.sendall(data)
            split = msg.split(" ")
            if split[0] == "PRIVMSG":
                #NICK!USER@HOST PRIVMSG #channel :msg
                channel = split[1]
                notifyMsg = "{}!{}@{} PRIVMSG {} :{} \r\n".format(currentClient.nick, currentClient.user, currentClient.addr, channel, msg.split(':')[1][:-3])
                
                manager.notify(addr[1], notifyMsg, NICK, split[1])
                print("RESPONSE ALL : {}".format(notifyMsg))
                logger.info("RESPONSE ALL : {}".format(notifyMsg))



def main(args):
    manager = clientManager()
    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = int(args[2]) if len(args) > 1 and args[1] == "-p" else 50007  #if -p arg ecists, the next arg will be added as the port
              # Arbitrary non-privileged port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        # s.settimeout(0.5)

        # s.setblocking(0)
        while True:
            try:
                conn, addr = s.accept()
                conn.send(b"connected")
                # threading.Thread(target=clientRun, args=(manager,conn, addr))
                start_new_thread(clientRun, (manager,conn, addr))
            except KeyboardInterrupt:
                print('kbinter')
                break

    print(manager.clients)



if __name__ == "__main__":
    # Parse your command line arguments here
    print(sys.argv)
    args = sys.argv
    main(args)