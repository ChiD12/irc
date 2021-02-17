import socket
import time
import threading
from _thread import *
import asyncio

async def runPrint(s):
    while True:
        try:
            data = s.recv(1024)
            await asyncio.sleep(1)
            print(data)
        except KeyboardInterrupt:
            s.sendall(b"close")
            break

async def runSend(s):
    while True:
        try:
            s.send(b'5555555555')
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            s.sendall(b"close")
            break

HOST = 'localhost'    # The remote host
PORT = 50007              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    # start_new_thread(runSend, (s,"j"))
    # time.sleep(1)
    # start_new_thread(runPrint, (s,"j"))

    async def inner_run():
            await asyncio.gather(
                runSend(s),
                runPrint(s),
                return_exceptions=True,
            )
    try:
        asyncio.run( inner_run() )
    except KeyboardInterrupt as e:
        "hi"
        
    
    
    
# print('Received', repr(data))