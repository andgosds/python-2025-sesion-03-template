import socket

SERVIDOR = "127.0.0.1"
PUERTO   = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mensaje = b"hola udp"
sock.sendto(mensaje, (SERVIDOR, PUERTO))        # envía datagrama
eco, _ = sock.recvfrom(1024)                    # espera eco
print("Servidor dice:", eco.decode())

sock.close()
