#!/usr/bin/env python3

from .command import CommandPacket

ATSHA204_DEFAULT_I2C_ADDR = 0x64

class CMD_DEVREV(CommandPacket):
    def __init__(self):
        CommandPacket.__init__(self,
            0x30,                       # OpCode
            0x00, (0x00, 0x00),
            response_size = 4
        )

class CMD_RANDOM(CommandPacket):

    MODE_NO_UPDATE_SEED = 0
    MODE_UPDATE_SEED = 1

    def __init__(self, mode):
        CommandPacket.__init__(self,
            0x1B,
            mode & 0xFF, (0x00, 0x00),
            response_size = 32
        )

class CMD_SHA(CommandPacket):

    MODE_INIT = 0
    MODE_COMPUTE = 1

    def __init__(self, mode, data=None):
        if mode & 1:
            assert type(data) is bytes and len(data) == 64
        else:
            data = bytes([])
        CommandPacket.__init__(self,
            0x47,
            mode & 0x01, (0x00, 0x00),
            data=data,
            response_size=1 if mode == 0 else 32
        )

class CMD_READ(CommandPacket):

    ZONE_CONFIG = 0
    ZONE_OTP = 1
    ZONE_DATA = 2
    READ_BYTES_4 = 0
    READ_BYTES_32 = 1

    def __init__(self, zone, address, read_bytes=0):
        param1 = (zone & 0b11) | ((read_bytes & 0b01) << 7)
        param2 = (address & 0xFF, (address & 0xFF00) >> 8)
        CommandPacket.__init__(self,
            0x02,
            param1, param2,
            data=bytes([]),
            response_size = 4 if 0 == read_bytes else 32
        )



if __name__ == "__main__":
    print(bytes(CMD_DEVREV()).hex())