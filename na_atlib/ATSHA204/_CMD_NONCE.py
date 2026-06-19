#!/usr/bin/env python3
from enum import IntEnum
from ..command import CommandPacket

class CMD_NONCE(CommandPacket):

    class Mode(IntEnum):
        INPUT_AND_UPDATE_EEPROM = 0
        INPUT_WITHOUT_UPDATE_EEPROM = 1
        PASSTHROUGH = 2


    def __init__(self, mode: Mode, numin: bytes):
        assert type(mode) is CMD_NONCE.Mode

        if mode == CMD_NONCE.Mode.PASSTHROUGH:
            assert type(numin) is bytes and len(numin) == 32
        else:
            assert type(numin) is bytes and len(numin) == 20


        CommandPacket.__init__(self,
            0x16,                       # OpCode
            int(mode) & 0b11, (0x00, 0x00),
            response_size = 1 if mode == CMD_NONCE.Mode.PASSTHROUGH else 32,
            data = numin
        )
