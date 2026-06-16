#!/usr/bin/env python3
from enum import IntEnum
from ..command import CommandPacket

class CMD_SHA(CommandPacket):

    class Mode(IntEnum):
        INIT    = 0
        COMPUTE = 1

    def __init__(self, mode: Mode, data=None):
        assert type(mode) is CMD_SHA.Mode
        
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
