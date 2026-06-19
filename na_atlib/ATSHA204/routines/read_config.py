#!/usr/bin/env python3

import time
from .._CMD_READ import CMD_READ
from .slot_config import SlotConfig

"""
 |                            SN<0:3>                      | 01 23 d9 f9
 |                            RevNum                       | 00 09 04 00
 |                            SN<4:7>                      | 39 76 28 5f
 |     SN<8>  |    ...       |  I2C_Enable  |    ...       | ee 0c 01 00
 |  I2C_Addr  |  CheckMacCfg |   OTPMode    | SelectorMode | c8 00 55 00
 |        SlotConfig 0       |         SlotConfig 1        | 8f 80 80 a1
 |        SlotConfig 2       |         SlotConfig 3        | 82 e0 a3 60
 |        SlotConfig 4       |         SlotConfig 5        | 94 40 a0 85
 |        SlotConfig 6       |         SlotConfig 7        | 86 40 87 07
 |        SlotConfig 8       |         SlotConfig 9        | 0f 00 89 f2
 |        SlotConfig 10      |         SlotConfig 11       | 8a 7a 0b 8b
 |        SlotConfig 12      |         SlotConfig 13       | 0c 4c dd 4d
 |        SlotConfig 14      |         SlotConfig 15       | c2 42 af 8f
 | UseFlag 0 | UpdateCount 0 | UseFlag 1 | UpdateCount 1   | ff 00 ff 00
 | UseFlag 2 | UpdateCount 2 | UseFlag 3 | UpdateCount 3   | ff 00 ff 00
 | UseFlag 4 | UpdateCount 4 | UseFlag 5 | UpdateCount 5   | ff 00 ff 00
 | UseFlag 6 | UpdateCount 6 | UseFlag 7 | UpdateCount 7   | ff 00 ff 00
 | LastKeyUse 0 ............................ LastKeyUse 3  | ff ff ff ff
 | LastKeyUse 4 ............................ LastKeyUse 7  | ff ff ff ff
 | LastKeyUse 8 ............................ LastKeyUse 11 | ff ff ff ff
 | LastKeyUse 12 ........................... LastKeyUse 15 | ff ff ff ff
 | UserExtra |    Selector   | LockValue |    LockConfig   | 00 00 55 55
"""

class ConfigZoneReader:

    def __init__(self, i2cbus):
        self.bus = i2cbus
        self.refresh()

    def _read_at(self, addr, short=False):
        cmd = CMD_READ(
            zone=CMD_READ.Zone.CONFIG, 
            address=addr,
            read_bytes=(\
                CMD_READ.ReadBytes.BYTES_4 if short \
                else CMD_READ.ReadBytes.BYTES_32\
            )
        )
        self.bus.write(bytes(cmd))
        time.sleep(0.08)
        reply = self.bus.read(cmd.response_size)
        parsed = cmd.parse_answer(reply)
        return parsed.payload

    def refresh(self):
        self.config = b''.join([
            self._read_at(0x00),
            self._read_at(0x08),
            self._read_at(0x10, True),
            self._read_at(0x11, True),
            self._read_at(0x12, True),
            self._read_at(0x13, True),
            self._read_at(0x14, True),
            self._read_at(0x15, True),
        ])

    @property
    def config_locked(self):
        return self.config[87] != 0x55

    @property
    def value_locked(self):
        return self.config[86] != 0x55

    @property
    def sn(self):
        return self.config[0:4] + self.config[8:13]

    def get_slotconfig(self, slot_id: int):
        assert type(slot_id) is int and (0 <= slot_id <= 15)
        offset = 20 + slot_id * 2
        value = self.config[offset:offset+2]
        return SlotConfig(value[0] + (value[1]<<8))