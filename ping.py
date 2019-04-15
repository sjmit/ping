#!/usr/bin/env python3

import socket
import sys
import os
import time
import struct


def main(argv):

    address = socket.gethostbyname(argv[0])
    system_id = os.getpid()
    sequence = 0

    header = struct.pack('BBHHH', 8, 0, 0xb809, system_id, sequence)
    header_size = struct.calcsize('BBHHH')

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        print("Error - Must be run as root")
    else:
        with s:
            s.settimeout(1)
            while True:
                
                data = struct.pack('d', 3.142)
                c = calculate_checksum(header + data)
                temp = struct.pack('BBHHH', 8, 0, c, system_id, sequence)
                packet = temp + data


                s.sendto(packet, (address, 1))
                #s.bind((socket.gethostname(), 7))  
                reply, return_addr = s.recvfrom(1024)

                # unpack starting at index 20 + header_size
                print(struct.unpack_from('d', reply[20+header_size:])[0])

                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break


if __name__ == "__main__":
    main(sys.argv[1:])