import socket
import sys
from os.path import join, isfile, isdir
from os import listdir, getcwd
import os
import mimetypes 

def response_ok(body=b"this is a pretty minimal response", mimetype=b"text/plain"):
    """returns a basic HTTP response"""
    resp = []
    resp.append(b"HTTP/1.1 200 OK")
    resp.append(b"Content-Type: " + mimetype)
    resp.append(b"")
    resp.append(body)
    return b"\r\n".join(resp)


def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return "\r\n".join(resp).encode('utf8')


def response_not_found():
    """returns a 404 Not Found response"""
    resp = []
    resp.append("HTTP/1.1 404 Not Found")
    resp.append("")
    return "\r\n".join(resp).encode('utf8')


def parse_request(request):
    first_line = request.split("\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    return uri


def handle_directory(uri):
    return ("\n".join(listdir(uri)).encode("utf8"), "text/plain".encode("utf8"))

def handle_file(uri):
    with open (uri, "rb") as file:
        contents = file.read()
        mime_type, _ =  mimetypes.guess_type(uri)
        return contents, mime_type.encode('utf8')


def resolve_uri(uri):
    cwd = getcwd() 
    absolute_path =  os.path.join(cwd, "webroot") + uri 
    if isdir(absolute_path):
        return handle_directory(absolute_path)
    if isfile(absolute_path):
        return handle_file(absolute_path)
    raise NameError


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)
                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')
                    if len(data) < 1024:
                        break

                try:
                    uri = parse_request(request)
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    try:
                        content, mime_type = resolve_uri(uri)
                        response = response_ok(content, mime_type)
                    except NameError:
                        response = response_not_found()
                    else:
                        response = response_ok(content, mime_type)
                print('sending response', file=log_buffer)
                conn.sendall(response)
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
