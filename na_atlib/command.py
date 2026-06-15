#!/usr/bin/env python3

from .ioblock import IOBlock



class ResponsePacket:

    def __init__(self, block):
        self._block = block

    @property
    def payload(self):
        return self._block.payload

    def __repr__(self):
        return "[ Type: ANS - %s ]" % repr(self._block)





class CommandPacket:

    def __init__(
        self,
        opcode,
        param1,
        param2: tuple,
        data=None,
        response_size=1
    ):
        assert type(opcode) is int
        self.opcode = opcode

        assert type(param1) is int
        self.param1 = param1

        param2 = bytes(list(param2))
        assert type(param2) is bytes and len(param2) == 2
        self.param2 = param2

        if not data is None:
            data = bytes(list(data))
        else:
            data = bytes([])
        assert type(data) is bytes
        self.data = data

        self._response_size = response_size

        self._io_block = IOBlock(bytes([
            self.opcode & 0xFF,
            self.param1 & 0xFF,
            self.param2[0],
            self.param2[1],
        ]) + self.data)

    def __bytes__(self):
        return bytes([
            0x03, # COMMAND
        ]) + bytes(self._io_block)

    def __repr__(self):
        return "[ Type: CMD - %s ]" % repr(self._io_block)

    @property
    def response_size(self):
        return self._response_size + 3

    def parse_answer(self, block):
        return ResponsePacket(self._io_block.parse_answer(block))

