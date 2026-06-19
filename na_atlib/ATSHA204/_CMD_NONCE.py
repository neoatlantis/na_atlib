#!/usr/bin/env python3

import hashlib
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

        mode = int(mode) & 0b11
        self.__tempkey_param = (numin, int(mode))

        CommandPacket.__init__(self,
            0x16,                       # OpCode
            mode, (0x00, 0x00),
            response_size = 1 if mode == CMD_NONCE.Mode.PASSTHROUGH else 32,
            data = numin
        )

    def get_tempkey(self, randout: bytes = None):
        if None != randout:
            assert type(randout) is bytes and len(randout) == 32

        if self.__tempkey_param[1] == int(CMD_NONCE.Mode.PASSTHROUGH):
            print("Debug: nonce passthrough")
            return self.__tempkey_param[0]

        return hashlib.sha256(b''.join([
            randout,
            self.__tempkey_param[0],
            b'\x16',
            bytes([self.__tempkey_param[1]]),
            b'\x00',
        ])).digest()