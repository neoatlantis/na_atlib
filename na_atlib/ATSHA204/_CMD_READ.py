#!/usr/bin/env python3
from enum import IntEnum
from ..command import CommandPacket

class CMD_READ(CommandPacket):

    class Zone(IntEnum):
        CONFIG = 0
        OTP    = 1
        DATA   = 2

    class ReadBytes(IntEnum):
        BYTES_4 = 0
        BYTES_32 = 1

    def __init__(self, zone: Zone, address, read_bytes: ReadBytes=0):
        param1 = (zone & 0b11) | ((read_bytes & 0b01) << 7)
        param2 = (address & 0xFF, (address & 0xFF00) >> 8)
        CommandPacket.__init__(self,
            0x02,
            param1, param2,
            data=bytes([]),
            response_size = 4 if 0 == read_bytes else 32
        )
