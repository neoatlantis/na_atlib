#!/usr/bin/env python3
from ..command import CommandPacket

class CMD_DEVREV(CommandPacket):
    def __init__(self):
        CommandPacket.__init__(self,
            0x30,                       # OpCode
            0x00, (0x00, 0x00),
            response_size = 4
        )