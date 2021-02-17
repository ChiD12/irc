import socket

host = 'www.httpbin.org/'
port = 80

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host,port))
        sock.sendall(b'GET /status/418 /HTTP/1.0\r\n\r\n')
        data= sock.recv(1024)

    print(data.decode('utf-8'))