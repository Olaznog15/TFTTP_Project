# Proyecto TFTP en Python (Servidor y Cliente)

Este proyecto implementa un **servidor y cliente TFTP (Trivial File Transfer Protocol)** utilizando únicamente sockets UDP y la librería estándar de Python, sin dependencias externas.  
Permite **subir archivos al servidor (WRQ)** y **descargar archivos del servidor (RRQ)** siguiendo la especificación básica del protocolo TFTP (RFC 1350).

---

## **Características**
- **Servidor TFTP**:
  - Responde a peticiones de lectura (RRQ) y escritura (WRQ).
  - Soporta transferencia de archivos en bloques de 512 bytes.
  - Implementación ligera y sin dependencias externas.
  - Gestión básica de errores con paquetes `ERROR` (opcode 5).
  - Configurable para ejecutarse en cualquier puerto UDP.

- **Cliente TFTP**:
  - Permite **subir archivos** al servidor con `WRQ`.
  - Permite **descargar archivos** desde el servidor con `RRQ`.
  - Maneja ACKs (opcode 4) y DATA (opcode 3) de acuerdo al protocolo.
  - Usa timeouts para evitar bloqueos si el servidor no responde.

---

## **Requisitos**
- **Python 3.7 o superior**.
- No se requieren librerías adicionales.

---

## **Estructura del Proyecto**
```
TFTP_Project/
│
├── Servidor/
│   └── TFTP_server.py
│   └── Archivos/
│
├── Cliente/
│   └── tftp_client.py
│   └── Archivos/
│
└── README.md
```

---

## **Cómo Ejecutar el Servidor**

1. Posicionarse en la carpeta `Servidor/`.
2. Ejecutar:
   ```bash
   python3 TFTP_server.py
   ```
3. Por defecto, el servidor escuchará en `127.0.0.1:6969`.  
   Puedes modificar `SERVER_IP` y `SERVER_PORT` en el código si deseas otro puerto o interfaz.

---

## **Cómo Subir un Archivo al Servidor**
En la carpeta `Cliente/` ejecuta:
```bash
python3 tftp_client.py upload <archivo_local>
```
He dejado un archivo de pruebas en la carpeta Archivos

Ejemplo:
```bash
python3 tftp_client.py upload Archivos/test.txt
```
Esto enviará el archivo `test.txt` al servidor TFTP en bloques de 512 bytes, esperando un `ACK` por cada bloque enviado. El archivo se guardara en la carpeta Archivos/ dentro de la carpeta Servidor

---

## **Cómo Descargar un Archivo del Servidor**
El cliente incluye una función `download_file()` para solicitar un archivo existente en el servidor:
```bash
python3 tftp_client.py download <archivo_remoto>
```
Ejemplo:
```bash
python3 tftp_client.py download test.txt
```
Esto pedirá el archivo `test.txt` y lo guardará en la carpeta Archivos/ dentro de Cliente.

---

## **Protocolo TFTP (Resumen)**
- **OPCODES:**
  - `1`: RRQ (Read Request)
  - `2`: WRQ (Write Request)
  - `3`: DATA
  - `4`: ACK
  - `5`: ERROR
- **Tamaño de bloque**: 512 bytes por defecto.
- **Fin de archivo**: Un bloque DATA con menos de 512 bytes indica el fin de la transferencia.

---

## **Posibles Errores y Soluciones**
- **"ACK inválido, cancelando."**  
  Esto ocurre si el servidor o el cliente no coinciden en el número de bloque. Asegúrate de que ambos incrementen el contador de bloque correctamente y de que se responda al mismo puerto origen.
  
- **"Tiempo de espera agotado."**  
  Puede deberse a que el servidor no recibió el paquete o no envió respuesta. Verifica el firewall y el puerto UDP.

---

## **Pruebas**
Para probar el sistema en local:
1. Ejecuta el servidor en una terminal:
   ```bash
   python3 TFTP_server.py
   ```
2. En otra terminal, ejecuta el cliente para subir o bajar archivos:
   ```bash
   python3 tftp_client.py upload test.txt
   python3 tftp_client.py download test.txt
   ```

---


## **Nota**
La idea es ejecutar el servidor y el cliente en ordenadores distintos pero como esto lo he hecho en un rato libre me ha dado pereza probarlo correctamente. En principio, modificando la ip del servidor y con las configuraciones correctas de la red no deberia haber problemas