#!/usr/bin/env python3

from na_atlib.ATSHA204 import *
from na_atlib.i2cbus import I2CBus



with I2CBus(1, ATSHA204_DEFAULT_I2C_ADDR) as bus:
    bus.wake()

    cmd = CMD_DEVREV()
    print(repr(cmd))

    print(bytes(cmd).hex())
    bus.write(bytes(cmd))
    reply = bus.read(33) #cmd.response_size)
    
    print(reply.hex())
    print(repr(cmd.parse_answer(reply)))
