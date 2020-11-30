#!/usr/bin/env python

import logging
import os
import sys
import struct

log = logging.getLogger(__name__)

XS_LIST = 1
XS_READ = 2
XS_WRITE = 11
XS_RM = 13
XS_ERROR = 16
XS_HDR_SZ = 16

NUL = b'\x00'


class XSOps(object):
    def __init__(self):
        self.vals = [XS_LIST, XS_READ, XS_WRITE, XS_RM]

    def __iter__(self):
        return iter(self.vals)


class ProcXenBus(object):

    def __enter__(self):
        self.fd = os.open("/proc/xen/xenbus", os.O_RDWR)
        self.ops = XSOps()
        self.rq_id = -1
        return self

    def __exit__(self, *exc_info):
        os.close(self.fd)

    #
    # Public methods
    #
    def read(self, path):
        self.__exec_cmd(XS_READ, path)
        (op, rq_id, tx_id, size) = self.__get_header()

        result = ''
        if self.__error_chk(XS_READ, op, size):
            return result
        return os.read(self.fd, size) if size > 0 else result

    def list(self, path):
        self.__exec_cmd(XS_LIST, path)
        (op, rq_id, tx_id, size) = self.__get_header()

        result = []
        if self.__error_chk(XS_LIST, op, size):
            return result

        if size > 0:
            data = os.read(self.fd, size)
            data = data.decode('utf-8').rstrip(NUL)
            for item in data.split(NUL):
                result.append(item)
        return result

    def write(self, path, data):
        self.__exec_cmd(XS_WRITE, path, data)
        (op, rq_id, tx_id, size) = self.__get_header()

        result = ''
        if self.__error_chk(XS_WRITE, op, size):
            return result

        if size > 0:
            status = os.read(self.fd, size)
            if status.decode('utf-8').rstrip(NUL) != b"OK":
                raise RuntimeError('write: unable to store value')
        return

    def delete(self, path):
        self.__exec_cmd(XS_RM, path)
        (op, rq_id, tx_id, size) = self.__get_header()

        result = ''
        if self.__error_chk(XS_RM, op, size):
            return result
        return os.read(self.fd, size) if size > 0 else result

    #
    # Private methods
    #
    def __exec_cmd(self, op, path, data=None):
        if op not in self.ops:
            raise ValueError('Invalid Operation Specified')

        if data is None:
            wlen = len(path) + 1
            wdat = path + NUL
        else:
            byts = bytes(data.decode('utf-8').rstrip(NUL))
            wlen = len(path) + 1 + len(byts)
            wdat = path + NUL + byts

        rq_id = self.__next_rq_id()
        os.write(self.fd, struct.pack("<IIII", op, rq_id, 0, wlen))
        os.write(self.fd, wdat)
        return

    def __get_header(self):
        header = os.read(self.fd, XS_HDR_SZ)
        return struct.unpack("<IIII", header)

    def __error_chk(self, cop, resop, resz):
        if resop == XS_ERROR:
            if resz > 0:
                msg = os.read(self.fd, resz)
                msg = msg.decode('utf-8').rstrip(NUL)
                log.debug('%s: got %s from xenstore',
                          self.__op_to_str(cop), msg)
            return -1
        elif resop != cop:
            log.debug('%s: xenstore returned bad op %d',
                      self.__op_to_str(cop), resop)
            if resz > 0:
                os.read(self.fd, resz)
            return -2
        return 0

    def __dump_header(self, header):
        (op, rq_id, tx_id, size) = struct.unpack("<IIII", header)
        print('   op: %s' % str(op))
        print('rq_id: %s' % str(rq_id))
        print('tx_id: %s' % str(tx_id))
        print(' size: %s' % str(size))
        return

    def __op_to_str(self, op):
        switch = {
            XS_LIST: "list()",
            XS_READ: "read()",
            XS_WRITE: "write()",
            XS_RM: "delete()",
            XS_ERROR: "Error"
        }
        return switch.get(op, 'Invalid Op')

    def __next_rq_id(self):
        self.rq_id += 1
        self.rq_id %= sys.maxsize
        return self.rq_id


if __name__ == "__main__":
    with ProcXenBus() as client:
        print('\n[[ test ]] listing contents of vm-data/networking\n')
        for mac in client.list("vm-data/networking"):
            print('MAC: %s' % mac)
            print(client.read("vm-data/networking/" + mac))

        print('\n[[ test ]] write/read to/from new key data/guest/foo\n')
        client.write("data/guest/foo", "bar-baz")
        print(client.read("data/guest/foo"))

        print('\n[[ test ]] delete/read of/from new key data/guest/foo\n')
        client.delete("data/guest/foo")
        print(client.read("data/guest/foo"))
