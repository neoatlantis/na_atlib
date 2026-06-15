#!/usr/bin/env python3

from na_atlib.ATSHA204 import *
from na_atlib.i2cbus import I2CBus
from na_atlib.help_sha256 import sha256_pad
import time



with I2CBus(1, ATSHA204_DEFAULT_I2C_ADDR) as bus:
    bus.wake()

    def call_command(name, cmd):
        print("** %s" % name)

        bus.write(bytes(cmd))
        time.sleep(0.1)
        reply = bus.read(cmd.response_size)
        print(reply.hex())

        parsed = cmd.parse_answer(reply)
        print(repr(parsed))
        return parsed

    call_command("Random", CMD_RANDOM(mode=1))

    # Now do SHA256 test

    test = b'abc'
    padded_test = sha256_pad(test)

    call_command("SHA", CMD_SHA(mode=0))
    hashed = call_command("SHA", CMD_SHA(mode=1, data=padded_test))
    assert hashed.payload == bytes.fromhex('ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
