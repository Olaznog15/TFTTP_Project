import socket
import struct
import os
import sys

SERVER_IP = "127.0.0.1"   # Cambia por la IP de tu servidor TFTP
SERVER_PORT = 6969        # Puerto del servidor
BLOCK_SIZE = 512

# Códigos de operación
OP_RRQ = 1
OP_WRQ = 2
OP_DATA = 3
OP_ACK = 4
OP_ERROR = 5

def send_rrq(sock, addr, filename, mode="octet"):
    """Envía una solicitud RRQ (Read Request)  al servidor."""
    packet = struct.pack("!H", OP_RRQ) + filename.encode() + b"\0" + mode.encode() + b"\0"
    sock.sendto(packet, addr)

def send_wrq(sock, addr, filename, mode="octet"):
    """Envía solicitud WRQ (Write Request) al servidor."""
    packet = struct.pack("!H", OP_WRQ) + filename.encode() + b"\0" + mode.encode() + b"\0"
    sock.sendto(packet, addr)

def send_data(sock, addr, block, data):
    """Envía un bloque de datos."""
    packet = struct.pack("!HH", OP_DATA, block) + data
    sock.sendto(packet, addr)

def send_ack(sock, addr, block):
    """Envía un ACK para un bloque recibido."""
    packet = struct.pack("!HH", OP_ACK, block)
    sock.sendto(packet, addr)

def download_file(filename, dest_path=None):
    """Descarga un archivo desde el servidor TFTP."""
    if dest_path is None:
        dest_path = filename

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5.0)
    server_addr = (SERVER_IP, SERVER_PORT)

    print(f"Descargando archivo '{filename}' desde {SERVER_IP}:{SERVER_PORT}...")

    # Enviar RRQ
    send_rrq(sock, server_addr, filename)

    with open(dest_path, "wb") as f:
        expected_block = 1
        while True:
            try:
                data, addr = sock.recvfrom(516)
            except socket.timeout:
                print("Tiempo de espera agotado (no respuesta del servidor).")
                break

            opcode = struct.unpack("!H", data[:2])[0]
            if opcode == OP_ERROR:
                print("Error del servidor:", data[4:].decode(errors="ignore"))
                break
            if opcode != OP_DATA:
                print("Respuesta inesperada del servidor.")
                break

            block = struct.unpack("!H", data[2:4])[0]
            if block != expected_block:
                print(f"Bloque inesperado (esperado {expected_block}, recibido {block}).")
                break

            # Guardar datos
            f.write(data[4:])
            send_ack(sock, addr, block)

            print(f"Bloque {block} recibido ({len(data[4:])} bytes).")

            if len(data[4:]) < BLOCK_SIZE:
                print("Descarga completada.")
                break

            expected_block += 1

    sock.close()

def upload_file(filename):
    if not os.path.isfile(filename):
        print(f"Error: El archivo '{filename}' no existe.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5.0)
    server_addr = (SERVER_IP, SERVER_PORT)

    print(f"Enviando archivo '{filename}' al servidor {SERVER_IP}:{SERVER_PORT}...")

    # Enviar WRQ
    send_wrq(sock, server_addr, os.path.basename(filename))

    # Esperar ACK 0
    try:
        data, _ = sock.recvfrom(516)
        opcode, block = struct.unpack("!HH", data[:4])
        if opcode == OP_ERROR:
            print("Error del servidor:", data[4:].decode(errors="ignore"))
            return
        if opcode != OP_ACK or block != 0:
            print("Respuesta inesperada del servidor.")
            return
    except socket.timeout:
        print("Tiempo de espera agotado (sin respuesta del servidor).")
        return

    # Enviar datos en bloques
    with open(filename, "rb") as f:
        block = 1
        while True:
            chunk = f.read(BLOCK_SIZE)
            send_data(sock, server_addr, block, chunk)

            try:
                ack, _ = sock.recvfrom(516)
                opcode, recv_block = struct.unpack("!HH", ack[:4])
                if opcode != OP_ACK or recv_block != block:
                    print("ACK inválido.")
                    break
            except socket.timeout:
                print("Tiempo de espera esperando ACK.")
                break

            print(f"Bloque {block} enviado ({len(chunk)} bytes).")

            if len(chunk) < BLOCK_SIZE:
                print("Archivo enviado completamente.")
                break

            block += 1

    sock.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso:")
        print("  python tftp_client.py upload <archivo>")
        print("  python tftp_client.py download <archivo>")
        sys.exit(1)

    action = sys.argv[1].lower()
    filename = sys.argv[2]

    if action == "upload":
        upload_file(filename)
    elif action == "download":
        download_file(filename)
    else:
        print("Acción desconocida:", action)
