#! /usr/bin/env python
# -*- coding:utf8 -*-

"""
Struct Format Characters List:

Format	    C Type	            Python type	        Standard size
x	        pad byte	        no value
c	        char	            string of length 1	    1
b	        signed char	        integer	                1
B	        unsigned char	    integer	                1
?	        _Bool	            bool	                1
h	        short	            integer	                2
H	        unsigned short	    integer	                2
i	        int	                integer	                4
I	        unsigned int	    integer	                4
l	        long	            integer	                4
L	        unsigned long	    integer	                4
q	        long long	        integer	                8
Q	        unsigned long long	integer	                8
f	        float	            float           	    4
d	        double	            float	                8
s	        char[]	            string
p	        char[]	            string
P	        void *	            integer
"""


import socket
import struct
import time
import select
import os
import sys

if sys.platform == "w32":
    default_timer = time.clock()
else:
    default_timer = time.time

ICMP_ECHO_REQUEST = 8


class PICMP:
    def __init__(self, dst_addr, timeout=2):
        self.dst_addr = dst_addr
        self.id = os.getpid()
        self.timeout = timeout

        try:
            icmp = socket.getprotobyname("icmp")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        except socket.error, (errno, msg):
            if errno == 1:
                msg += " - runner must be root"
                raise socket.error(msg)
            raise

    def __del__(self):
        self.sock.close()

    def send(self, times, interval=0.1):
        delay = []
        for _ in range(times):
            self._send_single()
            delay_once = self._recv_single()
            if delay_once is not None:
                delay_once *= 1000
            else:
                delay_once = 0
            delay_once = int(round(delay_once, 3))
            delay.append(delay_once)
            time.sleep(interval)
        return delay

    def _send_single(self):
        dst_addr = socket.gethostbyname(self.dst_addr)
        my_checksum = 0

        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, self.id, 1)
        bytes_in_double = struct.calcsize("d")
        data = (192 - bytes_in_double) * "Q"
        data = struct.pack("d", default_timer()) + data

        my_checksum = self.checksum(header + data)

        header = struct.pack(
            "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), self.id, 1
        )
        packet = header + data
        self.sock.sendto(packet, (dst_addr, 1))

    def _recv_single(self):
        time_left = self.timeout
        while True:
            start_time = default_timer()
            which_ready = select.select([self.sock], [], [], time_left)
            spend_time = (default_timer() - start_time)
            if not which_ready[0]:
                return

            recv_time = default_timer()
            packet, addr = self.sock.recvfrom(1024)
            icmp_header = packet[20:28]
            recv_type, code, checksum, packet_id, sequence = struct.unpack(
                "bbHHh", icmp_header
            )

            if recv_type != 8 and packet_id == self.id:
                bytes_in_double = struct.calcsize("d")
                time_sent = struct.unpack("d", packet[28:28 + bytes_in_double])[0]
                return recv_time - time_sent

            time_left -= spend_time
            if time_left <= 0:
                return

    @staticmethod
    def checksum(source_string):
        total = 0
        count_to = (len(source_string)/2) * 2
        count = 0

        while count < count_to:
            val = ord(source_string[count+1]) * 256 + ord(source_string[count])
            total += val
            total &= 0xffffffff
            count += 2

        if count_to < len(source_string):
            total += ord(source_string[len(source_string) - 1])
            total &= 0xffffffff

        total = (total >> 16) + (total & 0xffff)
        total += (total >> 16)
        answer = ~total
        answer &= 0xffff

        answer = answer >> 8 | (answer << 8 & 0xff00)

        return answer

    def _pack(self):
        pass

    def _unpack(self):
        pass


def main():
    p = PICMP("www.qq.com")
    print p.send(10)


if __name__ == "__main__":
    main()
