#!/usr/bin/env python3
from ..command import CommandPacket

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
