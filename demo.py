#!/usr/bin/env python3

from na_atlib.ATSHA204 import *
from na_atlib.i2cbus import I2CBus
import time



with I2CBus(1, ATSHA204_DEFAULT_I2C_ADDR) as bus:
    bus.wake()

    cmd = CMD_RANDOM(mode=1)
    print(repr(cmd))

    print(bytes(cmd).hex())
    cmdbytes = bytes(cmd)
    bus.write(cmdbytes)

    time.sleep(0.1)

    reply = bus.read(cmd.response_size)
    
    print(reply.hex())
    print(repr(cmd.parse_answer(reply)))
