#!/usr/bin/env python3
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