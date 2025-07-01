import socket
s = socket.socket() #Default type = SOCK_STREAM (TCP)


nombre = socket.gethostname()
puerto = 12345
s.bind((nombre, puerto))
print('Información del servidor: IP (',nombre,') Puerto (',puerto,')')
s.listen()
while True:
    c, addr = s.accept()
    print('Conexión recibida de ', addr)
    info = b'Gracias por conectar'
    print('Información enviada: ', info)
    c.send(info)
    print('Informacion recibida: ',c.recv(1024))
    info = b'El gusto es mio'
    print('Información enviada: ', info)
    c.send(info)
    c.close()