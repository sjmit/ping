import socket
import sys
import os

def send(conn, addr, ID):
    pass


def recv(conn):
    pass


def main(argv):

    hostname = socket.gethostbyname(argv[0])
    icmp = socket.getprotobyname("icmp")
    my_id = os.getpid()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except:
        print("Error opening socket connection")
    else:
        with s:
            pass


if __name__ == "__main__":
    main(sys.argv[1:])