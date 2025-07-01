import socket
s = socket.socket()
ip = "127.0.1.1"
puerto = 12345

host = socket.gethostname()
print("Hostname:", host, "→", socket.gethostbyname(host))

s.connect((ip, puerto))
print('Información recibida: ',s.recv(1024))
info = b'Ya me desconecto, un placer'
print('Información enviada: ', info)
s.send(info)
print('Información recibida: ',s.recv(1024))
s.close()