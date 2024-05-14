from io import TextIOWrapper
import socket
import threading
import os

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

# --- Server logic ---

def serve_client(sock:socket.socket):
    buf = sock.recv(BUFFER_SIZE).decode()
    method = parse_method(buf)

    # This server does not allow any HTTP methods other than GET
    if method != "GET":
        sock.send(write_404_header())
        sock.send("Only GET method is supported\n")
        sock.close()
        return

    path = parse_path(buf)
    # we replace '/' with '/index.html', because browsers are weird
    if path == "/":
        path += "index.html"
    # Where to find the file actually present in the filesystem
    file_path = ROOT + path

    if not os.path.isfile(file_path):
        print(threading.current_thread().name, "Could not load file at ", path)
        sock.send(write_404_header())
        sock.send((path + ": File not found").encode())
        sock.close()
        return # early exit from this function

    try:
        # We try first if it's a text file
        with open(file_path,"r") as f:
            text = f.read()
            sock.send(write_200_header())
            sock.send(text.encode())
    except UnicodeDecodeError:
        # If it's not a text file, send it as a binary file
        with open(file_path,"br") as f:
            binary = f.read()
            sock.send(write_200_header())
            sock.send(binary)
    finally:
        sock.close()

def main():
    # Creates a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        try:
            server.bind(ADDRESS)
            print("Server listening at", server.getsockname())
            server.listen()

            while True:
                # Receive a single connection
                sock,info = server.accept()
                print("Received Connection:", info)
                # Create new thread to serve the client
                t = threading.Thread(target=serve_client, args=(sock,))
                print("    Creating new thread with id:", t.name)
                t.start()
        except OSError as e:
            print("Could not bind socket to address",ADDRESS)
            print(e)
        except KeyboardInterrupt:
            print(" Closing down server...")

if __name__ == "__main__":
    main()

