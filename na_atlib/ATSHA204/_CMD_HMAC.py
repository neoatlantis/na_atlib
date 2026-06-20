#!/usr/bin/env python3
from enum import IntEnum
from ..command import CommandPacket

class CMD_HMAC(CommandPacket):

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

    def __init__(
        self,
        
        mode_SN_select :  SNSelect,
        mode_OTP_select:  OTPSelect,
        mode_source_flag: SourceFlag,

        slot_id,
    ):
        assert type(mode_SN_select)         is CMD_HMAC.SNSelect
        assert type(mode_OTP_select)        is CMD_HMAC.OTPSelect
        assert type(mode_source_flag)       is CMD_HMAC.SourceFlag

        assert type(slot_id) is int

        mode = (
            ((mode_SN_select & 1) << 6) |
            ((mode_OTP_select & 0b11) << 4) |
            ((mode_source_flag & 1) << 2)
        )
        self.__mode = mode

        CommandPacket.__init__(self,
            0x11,                       # OpCode
            mode, (slot_id & 0x0F, 0x00),
            response_size = 32
        )

    @property
    def mode(self): return self.__mode
