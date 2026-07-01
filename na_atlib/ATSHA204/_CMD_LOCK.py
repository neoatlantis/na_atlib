#!/usr/bin/env python3
from enum import IntEnum
from ..command import CommandPacket

class CMD_LOCK(CommandPacket):

    class Zone(IntEnum):
        CONFIG       = 0
        OTP_AND_DATA = 1

    class CRCCheck(IntEnum):
        CHECK = 0
        IGNORE = 1

    def __init__(self, zone: Zone, crc_check: CRCCheck, summary=0x0000):
        assert type(zone) is CMD_LOCK.Zone
        assert type(crc_check) is CMD_LOCK.CRCCheck

        param1 = ((int(crc_check) & 1) << 7) | int(zone)
        if crc_check == CMD_LOCK.CRCCheck.CHECK:
            assert type(summary) is int
        else:
            summary = 0

        CommandPacket.__init__(self,
            0x17,                       # OpCode
            param1, (summary & 0xFF, (summary & 0xFF00) >> 8),
            response_size = 1
        )
