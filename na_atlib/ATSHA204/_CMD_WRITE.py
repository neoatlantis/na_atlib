#!/usr/bin/env python3
from enum import IntEnum
import hashlib
from ..command import CommandPacket
from ..help_xor import xor_bytes

class CMD_WRITE(CommandPacket):

    class WriteBytes(IntEnum):
        BYTES_4 = 0
        BYTES_32 = 1

    class Encrypted(IntEnum):
        CLEARTEXT = 0
        ENCRYPTED = 1

    class Zone(IntEnum):
        CONFIG = 0
        OTP    = 1
        DATA   = 2 


    def __init__(
        self,
        zone: Zone,
        address,
        write_bytes: WriteBytes,
        plaintext_data: bytes,
        encrypted: Encrypted,
        tempkey: bytes=None
    ):
        assert type(zone) is CMD_WRITE.Zone
        assert type(write_bytes) is CMD_WRITE.WriteBytes
        assert type(encrypted) is CMD_WRITE.Encrypted
        assert type(plaintext_data) is bytes

        if encrypted == CMD_WRITE.Encrypted.ENCRYPTED:
            assert type(tempkey) is bytes and len(tempkey) == 32
            assert write_bytes == CMD_WRITE.WriteBytes.BYTES_32

        if write_bytes == CMD_WRITE.WriteBytes.BYTES_32:
            assert len(plaintext_data) == 32
        else:
            assert len(plaintext_data) == 4

        param1 = (
            (int(zone) & 0b11) |
            (int(encrypted & 1)<<6) |
            ((int(write_bytes) & 1) << 7)
        )
        param2 = (address & 0xFF, (address & 0xFF00) >> 8)


        mac = b''
        value = plaintext_data
        if encrypted == CMD_WRITE.Encrypted.ENCRYPTED:
            mac = self._calc_mac(tempkey, plaintext_data, param1, param2)
            value = xor_bytes(value, tempkey)

        CommandPacket.__init__(self,
            0x12,                       # OpCode
            param1, param2,
            data = value + mac,
            response_size = 1
        )

    def _calc_mac(self, tempkey, plaintext_data, param1, param2):
        return hashlib.sha256.digest(b''.join([
            tempkey,
            bytes([
                0x12,
                param1,
                param2 & 0xFF,
                (param2 & 0xFF00)>>8,
                0xEE,           # SN<8>
            ]),
            b'\x01\x23',        # SN<0:1>
            b'\x00'*25,
            plaintext_data,
        ]))
