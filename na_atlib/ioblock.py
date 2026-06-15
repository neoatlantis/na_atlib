#!/usr/bin/env python3

class IOBlock:

    # (count, data, crc16) as defined in Section 8.1

    def __init__(self, payload: bytes, acknowledged_count=0):
        assert type(payload) is bytes
        self.payload = bytes(list(payload))
        self._acknowledged_count = acknowledged_count

    @property
    def sending_count(self):
        # The count property in IO Block, if this block was to be sent
        # Notice this is NOT acknowledged bytes count, when this block was
        # received from remote!
        return 3 + len(self.payload)

    @property
    def acknowledged_count(self):
        # Bytes received by device. Device answers in same IO block format.
        return self._acknowledged_count


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
        crcdata = bytes([self.sending_count]) + self.payload
        crc16 = self._at_crc(crcdata)
        return crcdata + crc16

    def parse_answer(self, block):
        ackcount = block[0]
        crc16 = bytes(block[-2:])

        if ackcount != self.sending_count:
            raise Error("bytes-incomplete-received")

        if crc16 != self._at_crc(block[:-2]):
            raise Error("crc16-error")

        return IOBlock(block[1:-2], ackcount)

    def __repr__(self):
        if self.acknowledged_count > 0:
            return """[ %2d bytes << RECV : %s ]""" % (
                self.acknowledged_count, self.payload.hex())
        return """[ SEND >> %2d bytes : %s ]""" % (
            self.sending_count, self.payload.hex())
