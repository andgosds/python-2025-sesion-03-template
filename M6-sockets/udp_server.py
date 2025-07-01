import socket

IP      = "0.0.0.0"   # Escucha todas las interfaces
PUERTO  = 9999
BUFFER  = 1024        # Tamaño máximo del datagrama

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PUERTO))
print(f"Servidor UDP escuchando en {IP}:{PUERTO}")

while True:
    datos, addr = sock.recvfrom(BUFFER)         # recibe datagrama
    print(f"Recibido {datos!r} desde {addr}")
    sock.sendto(b"eco: " + datos, addr)         # responde al remitente
