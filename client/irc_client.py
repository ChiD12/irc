#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021
#
# Distributed under terms of the MIT license.

"""
Description:

"""
import asyncio
import logging
import sys

import patterns
import view
import socket

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()



class IRCClient(patterns.Subscriber):

    def __init__(self, s):
        super().__init__()
        self.username = str()
        self._run = True
        self.socket = s

    def set_view(self, view):
        self.view = view

    def set_user(self, msg):
        self.username = msg

    def update(self, msg):
        # Will need to modify this
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        # self.view.add_msg("test",msg)
        logger.info(f"IRCClient.update -> msg: {msg}")
        self.process_input(msg)
        

    def process_input(self, msg):
        # Will need to modify this
        self.add_msg(msg)
        if msg.lower().startswith('/quit'):
            # Command that leads to the closure of the process
            self.socket.sendall(str.encode("QUIT"))
            self.socket.close()
            raise KeyboardInterrupt
        else:
            self.socket.sendall(str.encode("PRIVMSG #global :{} \r\n".format(msg)))

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    def server_msg(self, msg):
        self.view.add_msg("server", msg)

    def on_start(self):
        self.view.add_msg("server"," what is your user?")

    async def run(self, s):
        """
        Driver of your IRC Client
        """

        connected = s.recv(1024).decode('utf-8')
        self.view.add_msg("server",connected)

        #loop until untaken nick/user
        while True:
            self.view.add_msg("server"," what is your user?")
            user = self.view.get_input().decode('utf-8')
            s.sendall(str.encode("NICK {} \r\n".format(user)))
            s.sendall(str.encode("USER {} 0 * :realname \r\n".format(user)))
            data = s.recv(1024).decode('utf-8')
            data = data.split(' ')
            if data[1] == "001":
                self.set_user(user)
                break
            elif data[1] == "433":
                self.view.add_msg("Server",(" ".join(data[4:-1]))[1:])
            
        #split up mixed up msges, also combine messages that were split     
        msgQ = []
        while True:
            s.settimeout(0.1)
            msg = ''
            
            try:
                msg = s.recv(1024).decode('utf-8')
                
            except socket.timeout:
                await asyncio.sleep(0.5)
            s.settimeout(None)
            if msg != '':

                split = msg.split('\r\n')
                if len(split) > 1:
                    for part in split:
                        if part != "":
                            msgQ.append(part+"\r\n")
                else:
                    msgQ.append(msg)

                #combine partial mesages until it ends with \r\n
                while msgQ[0][-2:] != "\r\n" and len(msgQ) != 1:
                    current = msgQ.pop(0)
                    msgQ[0] = current + msgQ[0]

                while len(msgQ) > 0 and msgQ[0][-2:] == "\r\n":
                    msg = msgQ.pop(0)
                    split = msg.split(" ")
                    if split[1] == "PRIVMSG":
                        user = msg.split('!')
                        msg = msg.split(':')
                        self.view.add_msg(user[0], msg[1][:-3])
                    if split[0] == "JOIN" or split[0] == "QUIT":

                        self.view.add_msg("Server", msg[5:-3])
            

    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass



def main(args):
    # Pass your arguments where necessary
    indexOfP = -1
    indexOfS = -1

    if "-s" in args:
        indexOfS = args.index("-s")

    if "-p" in args:
        indexOfP = args.index("-p")

    HOST = args[indexOfS+1] if indexOfS > -1 else 'localhost'   #if -p arg ecists, the next arg will be added as the port   
    PORT = int(args[indexOfP+1]) if indexOfP > -1 else 50007  #if -p arg ecists, the next arg will be added as the port 
    
    print(args)
    print(HOST)
    print(PORT)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        client = IRCClient(s)
        logger.info(f"Client object created")
        with view.View() as v:
            logger.info(f"Entered the context of a View object")
            client.set_view(v)
            logger.debug(f"Passed View object to IRC Client")
            v.add_subscriber(client)
            logger.debug(f"IRC Client is subscribed to the View (to receive user input)")

            async def inner_run():
                await asyncio.gather(
                    v.run(),
                    client.run(s),
                    return_exceptions=True,
                )
            try:
                asyncio.run( inner_run() )
            except KeyboardInterrupt as e:
                logger.debug(f"Signifies end of process")
    client.close()

if __name__ == "__main__":
    # Parse your command line arguments here
    args = sys.argv
    main(args)
