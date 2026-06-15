#!/usr/bin/env python3

from .errors import ATIOError

class IOBlock:

    # (count, data, crc16) as defined in Section 8.1

    def __init__(self, payload: bytes):
        assert type(payload) is bytes
        self.payload = bytes(list(payload))

    @property
    def count(self):
        # The count property in IO Block, if this block was to be sent
        return 3 + len(self.payload)

    def _at_crc(self, data: bytes) -> bytes:
        """
        计算 CRC-16 (多项式 0x8005, 初值 0x0000, 字节内 LSB 优先)
        返回小端字节序的 2 字节结果 (crc_le[0]=低字节, crc_le[1]=高字节)
        """
        crc_register = 0
        polynom = 0x8005

        for byte in data:
            # shift_register 从 0x01 开始左移，遍历该字节的 8 个位 (LSB 优先)
            shift_register = 0x01
            while shift_register <= 0xFF:
                data_bit = 1 if (byte & shift_register) else 0
                crc_bit = (crc_register >> 15) & 1
                crc_register = (crc_register << 1) & 0xFFFF  # 保持 16 位
                if data_bit != crc_bit:
                    crc_register ^= polynom
                shift_register <<= 1
        crc_le = bytes([crc_register & 0x00FF, (crc_register >> 8) & 0xFF])
        return crc_le

    def __bytes__(self):
        crcdata = bytes([self.count]) + self.payload
        crc16 = self._at_crc(crcdata)
        return crcdata + crc16

    def parse_answer(self, block):
        ackcount = block[0]
        crc16 = bytes(block[-2:])

        if block[0] == 4:
            errblock = block.rstrip(b'\xff')
            if (
                len(errblock) == 4 and \
                errblock[-2:] == self._at_crc(errblock[:-2])
            ):
                # we got an error block from AT device
                errcode = errblock[1]
                if 0 != errcode:
                    raise ATIOError(atsha204_errcode=errcode)

        if crc16 != self._at_crc(block[:-2]):
            raise Exception("crc16-error")

        return IOBlock(block[1:-2])

    def __repr__(self):
        return """< IOBlock :: %2d B (+3B overhead) : %s >""" % (
            self.count-3, self.payload.hex())
