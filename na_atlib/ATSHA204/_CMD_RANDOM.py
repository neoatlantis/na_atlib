#!/usr/bin/env python3
from enum import IntEnum
from ..command import CommandPacket

class CMD_RANDOM(CommandPacket):

    class Mode(IntEnum):
        NO_UPDATE_SEED = 0
        UPDATE_SEED    = 1

    def __init__(self, mode: Mode):
        CommandPacket.__init__(self,
            0x1B,
            mode & 0xFF, (0x00, 0x00),
            response_size = 32
        )
