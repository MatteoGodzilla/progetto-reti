import socket
import threading
import os
import sys

# --- Global variables ---
# relative path to where the static files are contained
ROOT="static"
# (Ip address, port) tuple where the server should listen.
# Might fail if the port is already taken
ADDRESS = ("localhost", 1234)
# Maximum size in bytes that can be read at once from the client
BUFFER_SIZE = 4096

# --- HTTP Utility classes ---
# Request
def parse_method(request:str)->str:
    return request.split(" ")[0]

def parse_path(request:str)->str:
    return request.split(" ")[1]

# Response
def write_200_header()->bytes:
    res = "HTTP/1.1 200 OK\r\n\r\n"
    return res.encode()

def write_404_header()->bytes:
    res = "HTTP/1.1 404 Not Found\r\n\r\n"
    return res.encode()

def write_405_header()->bytes:
    res = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
    return res.encode()

# --- Server logic ---

def serve_client(sock:socket.socket):
    buf = sock.recv(BUFFER_SIZE).decode()
    method = parse_method(buf)
    path = parse_path(buf)

    print(f"[{threading.current_thread().name}]: {method} {path}")

    # This server does not allow any HTTP methods other than GET
    if method != "GET":
        sock.send(write_405_header())
        sock.send("Only GET method is supported\n".encode())
        sock.close()
        return

    # we replace '/' with '/index.html', because browsers are weird
    if path == "/":
        path += "index.html"
    # Where to find the file actually present in the filesystem
    file_path = ROOT + path

    if not os.path.isfile(file_path):
        print(f"[{threading.current_thread().name}]: Could not load file at {file_path}")
        sock.send(write_404_header())
        sock.send(f"{path}: File not found".encode())
        sock.close()
        return # early exit from this function

    with open(file_path,"br") as f:
        bytes = f.read()
        sock.send(write_200_header())
        sock.send(bytes)
        sock.close()

def start_server():
    # Creates a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        try:
            server.bind(ADDRESS)
            print(f"Server listening at {server.getsockname()} ({ROOT})")
            server.listen()

            while True:
                # Receive a single connection
                sock, info = server.accept()
                print(f"Received Connection: {info}")
                # Create new thread to serve the client
                t = threading.Thread(target=serve_client, args=(sock,))
                print(f"    Creating new thread with id: {t.name}")
                t.start()
        except OSError as e:
            print(f"Could not bind socket to address {ADDRESS}")
            print(e)
        except KeyboardInterrupt:
            print(" Closing down server...")

def usage():
    print("Options available:")
    print("-h, --help: shows this help message")
    print(f"-a ADDRESS, --address=ADDRESS: specify the address used for this server. Default is {ADDRESS[0]}")
    print(f"-p PORT, --port=PORT: specify the port used for this server. Default is {ADDRESS[1]}")
    print(f"-r ROOT, --root=ROOT: specify where the root folder for serving files is located in the filesystem. Default is {ROOT}")
    sys.exit(1) # We force close the application as to not start the server

# This CLI parsing should really be replaced with a proper library
def parse_cli_args():
    if len(sys.argv) == 1:
        # The user did not specify any parameter, so there's nothing to do
        return

    # We have to tell python that we want to modify the variable that already exists
    # instead of creating a local variable
    global ADDRESS
    global ROOT
    argc = len(sys.argv)
    for i, val in enumerate(sys.argv):
        if val == "-h" or val == "--help":
            usage()
        # Ip address
        if val == "-a" and i + 1 < argc:
            ADDRESS = (sys.argv[i+1], ADDRESS[1])
        if val.startswith("--address="):
            tokens = val.split("=")
            ADDRESS = (tokens[1], ADDRESS[1])
        # Port
        if val == "-p" and i + 1 < argc:
            ADDRESS = (ADDRESS[0], int(sys.argv[i+1]))
        if val.startswith("--port="):
            tokens = val.split("=")
            ADDRESS = (ADDRESS[0], int(tokens[1]))
        # Root
        if val == "-r" and i + 1 < argc:
            ROOT = sys.argv[i+1]
        if val.startswith("--root="):
            tokens = val.split("=")
            ROOT = tokens[1]

def main():
    parse_cli_args()
    start_server()

if __name__ == "__main__":
    main()

