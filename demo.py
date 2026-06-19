#!/usr/bin/env python3

from na_atlib.ATSHA204 import DEFAULT_I2C_ADDR as ATSHA204_DEFAULT_I2C_ADDR
from na_atlib.ATSHA204.commands import *
from na_atlib.ATSHA204.routines.read_config import ConfigZoneReader
from na_atlib.i2cbus import I2CBus
from na_atlib.help_sha256 import sha256_pad
import time
import hashlib


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

    config_zone_reader = ConfigZoneReader(bus)
    config_zone = config_zone_reader.config
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
        h = config_zone[4*i:4*i+4].hex()
        print("0x%02X" % i, names[i].rjust(60, " "), h[:2], h[2:4], h[4:6], h[6:8])

    print("Device SN: %s" % config_zone_reader.sn.hex())
    print("Config zone locked: %s" % ("Yes" if config_zone_reader.config_locked else "No"))
    print("Data & OTP zone locked: %s" % ("Yes" if config_zone_reader.value_locked else "No"))

    for i in range(0, 16):
        slot_config = config_zone_reader.get_slotconfig(i)
        print("Slot %2d config: %s" % (i, repr(slot_config)))


    # Test nonce

    ret = call_command(
        "NONCE",
        CMD_NONCE(mode=CMD_NONCE.Mode.INPUT_WITHOUT_UPDATE_EEPROM, numin=b'0'*20)
    )
    print(ret.hex())

    # Test MAC on slot 0
    challenge = b'\x00'*32

    ret = call_command(
        "MAC on slot 0 with challenge",
        CMD_MAC(
            mode_SN_select   = CMD_MAC.SNSelect.NO_SN,
            mode_OTP_select  = CMD_MAC.OTPSelect.NO_OTP,
            mode_source_flag = CMD_MAC.SourceFlag.INPUT,
            mode_SHA_first_source = CMD_MAC.SHAFirstSource.SLOT,
            mode_SHA_second_source= CMD_MAC.SHASecondSource.CHALLENGE,
            slot_id=0,
            challenge=challenge,
        )
    )
    print('IC returned  :', ret.hex())
    print('We calculated:', hashlib.sha256(b''.join([
        bytes.fromhex('0000A1AC57FF404E45D40401BD0ED3C673D3B7B82D85D9F313B55EDA3D940000'),
        challenge,
        b'\x08',
        bytes([0b00000100]),
        bytes([0x00, 0x00]),
        b'\x00'*11,
        b'\xee',
        b'\x00'*4,
        b'\x01\x23',
        b'\x00'*2,
    ])).digest().hex())


    # Configure slot 2 & 3 using Write command
    # -- slot 2 is auth key for slot 3, intended to copy slot 3 into tempkey
    #    when slot 2 is authed.
    # -- this requires slot 2 must have ReadKey == 0

    slot2config = config_zone_reader.get_slotconfig(2)
    slot3config = config_zone_reader.get_slotconfig(3)
    slot2old = bytes(slot2config)
    slot3old = bytes(slot3config)

    print('Slot 2 Config HEX:', bytes(slot2config).hex())
    print('Slot 2 Config - Readkey:', slot2config.read_key)
    print('Slot 2 Config - CheckOnly', slot2config.check_only)

    if slot2config.read_key != 0:
        slot2config.read_key = 0

    if slot2config.check_only != 1:
        slot2config.check_only = 1
    
    print('Slot 2 Config HEX new:', bytes(slot2config).hex())

    print('Slot 3 Config HEX:', bytes(slot3config).hex())

    if slot3config.limited_use != 0:
        slot23needupdate = True
        slot3config.limited_use = 0

    print('Slot 3 Config HEX new:', bytes(slot3config).hex())


    if bytes(slot2config) != slot2old or bytes(slot3config) != slot3old:
        call_command(
            "Update slot 2 and 3 config",
            CMD_WRITE(
                zone = CMD_WRITE.Zone.CONFIG,
                address = 0x06,
                write_bytes = CMD_WRITE.WriteBytes.BYTES_4,
                plaintext_data = bytes(slot2config) + bytes(slot3config),
                encrypted = CMD_WRITE.Encrypted.CLEARTEXT
            )
        )