import os
import socket
import struct

TFTP_PORT = 6969
TFTP_DIR = "Servidor/Archivos"
BLOCK_SIZE = 512

# Códigos de operación
OP_RRQ = 1
OP_WRQ = 2
OP_DATA = 3
OP_ACK = 4
OP_ERROR = 5

# Generamos una carpeta si no existe
os.makedirs(TFTP_DIR, exist_ok=True)

def send_ack(sock, addr, block):
    packet = struct.pack("!HH", OP_ACK, block)
    sock.sendto(packet, addr)

def send_error(sock, addr, code, message):
    packet = struct.pack("!HH", OP_ERROR, code) + message.encode() + b'\0'
    sock.sendto(packet, addr)

def handle_wrq(sock, addr, filename):
    """Maneja subida de archivos (WRQ)."""
    path = os.path.join(TFTP_DIR, filename)
    print(f"Cliente {addr} quiere subir {filename} -> {path}")

    with open(path, "wb") as f:
        block = 0
        send_ack(sock, addr, block)  # ACK inicial
        while True:
            try:
                data, _ = sock.recvfrom(516)
                opcode, recv_block = struct.unpack("!HH", data[:4])
                if opcode != OP_DATA:
                    print("Paquete inesperado, cancelando.")
                    break
                if recv_block != block + 1:
                    print("Bloque fuera de orden.")
                    break
                f.write(data[4:])
                block += 1
                send_ack(sock, addr, block)
                if len(data[4:]) < BLOCK_SIZE:
                    print(f"Archivo {filename} recibido correctamente.")
                    print(f"Servidor TFTP escuchando en puerto {TFTP_PORT} (carpeta: {TFTP_DIR})")
                    break
            except socket.timeout:
                print("Timeout esperando datos, abortando WRQ.")
                break

def handle_rrq(sock, addr, filename):
    """Maneja descarga de archivos (RRQ)."""
    path = os.path.join(TFTP_DIR, filename)
    if not os.path.isfile(path):
        send_error(sock, addr, 1, "File not found")
        return

    print(f"Cliente {addr} descargando {filename}")
    with open(path, "rb") as f:
        block = 1
        while True:
            data = f.read(BLOCK_SIZE)
            packet = struct.pack("!HH", OP_DATA, block) + data
            sock.sendto(packet, addr)
            try:
                ack, _ = sock.recvfrom(516)
                opcode, recv_block = struct.unpack("!HH", ack[:4])
                if opcode != OP_ACK or recv_block != block:
                    print("ACK inválido, cancelando.")
                    break
            except socket.timeout:
                print("Timeout esperando ACK, cancelando RRQ.")
                break
            if len(data) < BLOCK_SIZE:
                print(f"Archivo {filename} enviado completo.")
                break
            block += 1

def start_tftp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", TFTP_PORT))
    sock.settimeout(10.0)  # Para evitar bloqueos eternos

    print(f"Servidor TFTP escuchando en puerto {TFTP_PORT} (carpeta: {TFTP_DIR})")

    while True:
        try:
            data, addr = sock.recvfrom(516)
            opcode = struct.unpack("!H", data[:2])[0]
            filename = data[2:].split(b"\0", 1)[0].decode(errors="ignore")
            print(f"Solicitud de {addr}: {filename} (opcode {opcode})")

            if opcode == OP_RRQ:
                handle_rrq(sock, addr, filename)
            elif opcode == OP_WRQ:
                handle_wrq(sock, addr, filename)
            else:
                send_error(sock, addr, 4, "Illegal TFTP operation")

        except socket.timeout:
            # El servidor sigue corriendo aunque no reciba nada
            continue
        except KeyboardInterrupt:
            print("Servidor detenido por el usuario.")
            break

if __name__ == "__main__":
    start_tftp_server()
