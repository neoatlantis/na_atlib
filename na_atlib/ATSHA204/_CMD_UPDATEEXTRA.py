#!/usr/bin/env python3
from enum import IntEnum
from ..command import CommandPacket

class CMD_UPDATEEXTRA(CommandPacket):

    class Mode(IntEnum):
        UPDATE_BYTE_84                  = 0
        UPDATE_BYTE_85                  = 1
        DECREMENT_LIMITED_USE_COUNTER   = 0b10

    def __init__(self, mode: Mode, newvalue):
        assert type(mode) is CMD_UPDATEEXTRA.Mode
        assert type(newvalue) is int

        CommandPacket.__init__(self,
            0x20,                       # OpCode
            int(mode), (newvalue & 0xFF, 0x00),
            response_size = 1
        )
