#!/usr/bin/env python3
from enum import IntEnum
from ..command import CommandPacket

class CMD_CHECKMAC(CommandPacket):

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
        CLIENTCHAL = 0
        TEMPKEY    = 1


    def __init__(
        self,
        
        mode_OTP_select:  OTPSelect,
        mode_source_flag: SourceFlag,
        mode_SHA_first_source: SHAFirstSource,
        mode_SHA_second_source: SHASecondSource,

        slot_id,

        clientchal,
        clientresp,
        otherdata,  # otherdata from the other's device, must be constructed
                    # as in datasheet Table 8-10
    ):
        assert type(mode_OTP_select)        is CMD_CHECKMAC.OTPSelect
        assert type(mode_source_flag)       is CMD_CHECKMAC.SourceFlag
        assert type(mode_SHA_first_source)  is CMD_CHECKMAC.SHAFirstSource
        assert type(mode_SHA_second_source) is CMD_CHECKMAC.SHASecondSource

        assert type(slot_id) is int

        assert type(clientchal) is bytes and len(clientchal) == 32
        assert type(clientresp) is bytes and len(clientresp) == 32
        assert type(otherdata)  is bytes and len(otherdata)  == 13

        mode = (
            ((mode_OTP_select & 0b11) << 4) |
            ((mode_source_flag & 1) << 2) |
            ((mode_SHA_first_source & 1) << 1) |
            (mode_SHA_second_source & 1)
        )

        CommandPacket.__init__(self,
            0x28,                       # OpCode
            mode, (0x00, slot_id & 0x0F),
            data = clientchal+clientresp+otherdata,
            response_size = 1
        )
