from io import TextIOWrapper
from socket import *
import threading
import os

# Global variables
# relative path to where the static files are contained
ROOT="static"
# (Ip address, port) tuple where the server should listen
ADDRESS = ("localhost", 1234)
# Maximum size in bytes that can be read at once from the client
BUFFER_SIZE = 4096

# HTTP Utility classes
# Request
def parse_method(request:str)->str:
    return request.split(" ")[0]

def parse_path(request:str)->str:
    return request.split(" ")[1]

# Response
def write_200_response(data:str)->bytes:
    res = "HTTP/1.1 200 OK\r\n\r\n"
    res += data
    return res.encode()

def write_404_response(data:str)->bytes:
    res = "HTTP/1.1 404 Not Found\r\n\r\n"
    res += data
    return res.encode()

# Server logic
def read_bytes_file(file: TextIOWrapper)->bytes:
    pass

def serve_client(socket:socket, info):
    buf = socket.recv(BUFFER_SIZE).decode()
    method = parse_method(buf)

    # This server does not allow any HTTP methods other than GET
    if method != "GET":
        response = write_404_response("Only GET method is supported\n")
        socket.send(response)
        socket.close()
        return

    path = parse_path(buf)
    # we replace '/' with '/index.html'
    if path == "/":
        path += "index.html"

    if not os.path.isfile(ROOT+path):
        print(threading.current_thread().name, "Could not load file at ", path)
        print(e)
        response = write_404_response(path + ": File not found")
        socket.send(response)
        socket.close()
        return

    try:
        # We try first if it's a text file
        with open(ROOT + path,"r") as f:
            text = f.read()
            response = write_200_response(text)
            socket.send(response)
    except UnicodeDecodeError:
        # If it's not a text file, it probably is a binary file
        with open(ROOT + path,"br") as f:
            binary = f.read()
            response = write_200_response("")
            socket.send(response)
            socket.send(binary)
    finally:
        socket.close()

if __name__ == "__main__":
    # Creates a TCP socket
    server = socket(AF_INET, SOCK_STREAM)
    try:
        server.bind(ADDRESS)
        print("Server listening at", ADDRESS)
        server.listen()

        while True:
            # Receive a single connection
            sock,info = server.accept()
            print("Received Connection:", info)
            # Create new thread to serve the client
            t = threading.Thread(target=serve_client, args=(sock,info))
            print("\tCreating new thread with id:", t.name)
            t.start()
    except OSError as e:
        print("Could not bind socket to address",ADDRESS)
        print(e)
        pass

