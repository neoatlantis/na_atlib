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



if __name__ == "__main__":
    print(bytes(CMD_DEVREV()).hex())
