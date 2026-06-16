#!/usr/bin/env python3

from na_atlib.ATSHA204 import DEFAULT_I2C_ADDR as ATSHA204_DEFAULT_I2C_ADDR
from na_atlib.ATSHA204.commands import *
from na_atlib.i2cbus import I2CBus
from na_atlib.help_sha256 import sha256_pad
import time



with I2CBus(1, ATSHA204_DEFAULT_I2C_ADDR) as bus:
    bus.wake()

    def call_command(name, cmd, silence=False):
        if not silence:
            print("** %s" % name)

        bus.write(bytes(cmd))
        time.sleep(0.08)
        reply = bus.read(cmd.response_size)
        #print(reply.hex())

        parsed = cmd.parse_answer(reply)
        
        if not silence:
            print(repr(parsed))
        return parsed.payload

    call_command("Random", CMD_RANDOM(mode=CMD_RANDOM.Mode.NO_UPDATE_SEED))

    # Now do SHA256 test

    test = b'abc'
    padded_test = sha256_pad(test)

    call_command(
        "SHA",
        CMD_SHA(mode=CMD_SHA.Mode.INIT)
    )
    hashed = call_command(
        "SHA",
        CMD_SHA(mode=CMD_SHA.Mode.COMPUTE, data=padded_test)
    )
    assert hashed == bytes.fromhex('ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')

    # Do some reads
    print("** CONFIG ZONE")

    names = [
        "|                            SN<0:3>                      |",
        "|                            RevNum                       |",
        "|                            SN<4:7>                      |",
        "|     SN<8>  |    ...       |  I2C_Enable  |    ...       |",
        "|  I2C_Addr  |  CheckMacCfg |   OTPMode    | SelectorMode |",
        "|        SlotConfig 0       |         SlotConfig 1        |",
        "|        SlotConfig 2       |         SlotConfig 3        |",
        "|        SlotConfig 4       |         SlotConfig 5        |",
        "|        SlotConfig 6       |         SlotConfig 7        |",
        "|        SlotConfig 8       |         SlotConfig 9        |",
        "|        SlotConfig 10      |         SlotConfig 11       |",
        "|        SlotConfig 12      |         SlotConfig 13       |",
        "|        SlotConfig 14      |         SlotConfig 15       |",
        "| UseFlag 0 | UpdateCount 0 | UseFlag 1 | UpdateCount 1   |",
        "| UseFlag 2 | UpdateCount 2 | UseFlag 3 | UpdateCount 3   |",
        "| UseFlag 4 | UpdateCount 4 | UseFlag 5 | UpdateCount 5   |",
        "| UseFlag 6 | UpdateCount 6 | UseFlag 7 | UpdateCount 7   |",
        "| LastKeyUse 0 ............................ LastKeyUse 3  |",
        "| LastKeyUse 4 ............................ LastKeyUse 7  |",
        "| LastKeyUse 8 ............................ LastKeyUse 11 |",
        "| LastKeyUse 12 ........................... LastKeyUse 15 |",
        "| UserExtra |    Selector   | LockValue |    LockConfig   |"

    ]
    for i in range(0, len(names)):
        if i % 3:
            bus.idle()
            bus.wake()

        cfgdata = call_command(
            "READ",
            CMD_READ(
                zone=CMD_READ.Zone.CONFIG, 
                address=i,
                read_bytes=CMD_READ.ReadBytes.BYTES_4
            ),
            silence=True
        )
        h = cfgdata.hex()
        print(names[i].rjust(60, " "), h[:2], h[2:4], h[4:6], h[6:8])

