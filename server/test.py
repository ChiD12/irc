import socket

HOST = 'localhost'    # The remote host
PORT = 50007              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    for i in range(6):
        s.send(b'Hello, world')
    s.sendall(b"hi")
    data = s.recv(1024)
    print(data)
    s.sendall(b"hi2")
    data = s.recv(1024)
    print(data)
    s.sendall(b"close")
    
print('Received', repr(data))