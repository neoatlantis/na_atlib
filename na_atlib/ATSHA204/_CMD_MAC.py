#!/usr/bin/env python3
import hashlib
from enum import IntEnum
from ..command import CommandPacket

class CMD_MAC(CommandPacket):

    class SNSelect(IntEnum):
        NO_SN  = 0
        USE_SN = 1

    class OTPSelect(IntEnum):
        OTP_BYTES_11 = 0b11
        OTP_BYTES_8  = 0b10
        NO_OTP       = 0b00

    class SourceFlag(IntEnum):
        RAND       = 0
        INPUT      = 1

    class SHAFirstSource(IntEnum):
        SLOT       = 0
        TEMPKEY    = 1

    class SHASecondSource(IntEnum):
        CHALLENGE  = 0
        TEMPKEY    = 1


    def __init__(
        self,
        
        mode_SN_select :  SNSelect,
        mode_OTP_select:  OTPSelect,
        mode_source_flag: SourceFlag,
        mode_SHA_first_source: SHAFirstSource,
        mode_SHA_second_source: SHASecondSource,

        slot_id,
        challenge = None
    ):
        assert type(mode_SN_select)         is CMD_MAC.SNSelect
        assert type(mode_OTP_select)        is CMD_MAC.OTPSelect
        assert type(mode_source_flag)       is CMD_MAC.SourceFlag
        assert type(mode_SHA_first_source)  is CMD_MAC.SHAFirstSource
        assert type(mode_SHA_second_source) is CMD_MAC.SHASecondSource

        assert type(slot_id) is int
        if challenge is not None:
            assert type(challenge) is bytes and len(challenge) == 32

        mode = (
            ((mode_SN_select & 1) << 6) |
            ((mode_OTP_select & 0b11) << 4) |
            ((mode_source_flag & 1) << 2) |
            ((mode_SHA_first_source & 1) << 1) |
            (mode_SHA_second_source & 1)
        )
        self.__mode = mode
        self.__slot_id = slot_id & 0x0F
        self.__mode_SN_select = mode_SN_select
        self.__mode_OTP_select = mode_OTP_select

        CommandPacket.__init__(self,
            0x08,                       # OpCode
            mode, (slot_id & 0x0F, 0x00),
            response_size = 32,
            data = (
                b''\
                if mode_SHA_second_source == CMD_MAC.SHASecondSource.TEMPKEY\
                else challenge
            )
        )

    @property
    def mode(self): return self.__mode

    def calculate_response(self, key, challenge, sn, otp=b'\x00' * 11):
        """
        Calculate the expected MAC response off-chip for verification.

        key:       32-byte first SHA source (slot key value or TempKey contents)
        challenge: 32-byte second SHA source (challenge input or TempKey contents)
        sn:        9-byte device serial number (SN[0..8]); SN[0:2] == 0x0123
                   and SN[8] == 0xEE are fixed for all ATSHA204 devices
        otp:       OTP zone data (at least 11 bytes); only used when OTPSelect
                   is not NO_OTP
        """
        assert type(key)       is bytes and len(key)       == 32
        assert type(challenge) is bytes and len(challenge) == 32
        assert type(sn)        is bytes and len(sn)        == 9

        if self.__mode_OTP_select == CMD_MAC.OTPSelect.OTP_BYTES_11:
            otp_part = bytes(otp[0:11])
        elif self.__mode_OTP_select == CMD_MAC.OTPSelect.OTP_BYTES_8:
            otp_part = bytes(otp[0:8]) + b'\x00' * 3
        else:
            otp_part = b'\x00' * 11

        # SN[8] and SN[0:2] are always included (fixed factory constants on ATSHA204).
        # SN[4:8] and SN[2:4] are included only when SNSelect.USE_SN is set.
        use_sn = self.__mode_SN_select == CMD_MAC.SNSelect.USE_SN
        sn4to7 = sn[4:8] if use_sn else b'\x00' * 4
        sn2to3 = sn[2:4] if use_sn else b'\x00' * 2

        return hashlib.sha256(b''.join([
            key,
            challenge,
            b'\x08',
            bytes([self.__mode]),
            bytes([self.__slot_id, 0x00]),
            otp_part,
            sn[8:9],
            sn4to7,
            sn[0:2],
            sn2to3,
        ])).digest()