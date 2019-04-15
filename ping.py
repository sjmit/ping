#!/usr/bin/env python3

import socket
import sys
import os
import time
import struct


MAX_BUFF_SIZE = 1024
ICMP_ECHO_TYPE = 8
ICMP_ECHO_CODE = 0


# From https://github.com/emamirazavi/python3-ping/blob/master/ping.py

def calculate_checksum(source_string):

    s = 0
    num_bytes = len(source_string)

    # Add high and low bytes of each word in bytearray
    # This currently only works for even numbered bytearrays
    for i in range(0, num_bytes, 2):
        s += source_string[i] * 256 + source_string[i + 1]

    s = (s >> 16) + (s & 0xFFFF)  # Add high 16 and low 16 bits
    s += (s >> 16)                # Add carry, if any     
    s = ~s & 0xFFFF               # Invert and mask to 16 bits

    return s
        

def main(arguments):

    address = socket.gethostbyname(arguments[0])
    system_id = os.getpid() & 0xFFFF
    sequence = 0
    header_size = struct.calcsize('BBHHH')

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        print("Permission Error - Must be run as root")
        return

    with s:
        s.settimeout(1)
        while True:
            
            # Create a dummy header
            header = struct.pack('!BBHHH', 
                                 ICMP_ECHO_TYPE,
                                 ICMP_ECHO_CODE,
                                 0,
                                 system_id,
                                 sequence)

            # Generate a timestamp and use it and the dummy
            # header to calculate checksum
            data = struct.pack('d', time.time())
            checksum = calculate_checksum(header + data)

            # Create a new header with the calculated checksum
            header = struct.pack('!BBHHH', 
                                 ICMP_ECHO_TYPE,
                                 ICMP_ECHO_CODE,
                                 checksum,
                                 system_id,
                                 sequence)

            packet = header + data

            # Send packet and wait for reply. Port number doesn't matter
            s.sendto(packet, (address, 1))
            try:
                reply, return_addr = s.recvfrom(MAX_BUFF_SIZE)
            except socket.timeout:
                print("Timeout Error - destination unreachable")
                continue

            # Calculate ping elapsed time in ms
            previous_time = struct.unpack_from('d', reply[20+header_size:])[0]
            ping_time_ms = (time.time() - previous_time) * 100

            # Print ping results to console
            print("{0} bytes from {1}: seq={3} time={2:.2f} ms".format(len(reply), address, ping_time_ms, sequence))
            
            sequence += 1

            # Wait one second between pings. Closes program with ctrl+C
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nExiting...")
                break


if __name__ == "__main__":
    main(sys.argv[1:])