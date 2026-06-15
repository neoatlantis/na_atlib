#!/usr/bin/env python3

class ATIOError(IOError):

    atsha204_errcode = 0
    atsha204_error_checkmac_mismatch = False
    ataha204_error_parse = False
    atsha204_error_execution = False
    atsha204_error_after_wake_prior_command = False
    atsha204_error_crc = False


    def __init__(
        self,
        atsha204_errcode=0
    ):
        IOError.__init__(self)

        self.atsha204_errcode = atsha204_errcode

        self.atsha204_error_checkmac_mismatch = 0x01 == atsha204_errcode
        self.ataha204_error_parse = 0x03 == atsha204_errcode
        self.atsha204_error_execution = 0x0F == atsha204_errcode
        self.atsha204_error_after_wake_prior_command = 0x11 == atsha204_errcode
        self.atsha204_error_crc = 0xFF == atsha204_errcode

    def __repr__(self):
        text = [
            "ATSHA204Error: 0x%2X" % self.atsha204_errcode\
                if self.atsha204_errcode else "",
        ]
        for flag in [
            "checkmac_mismatch",
            "parse",
            "execution",
            "after_wake_prior_command",
            "crc"
        ]:
            attrname = "atsha204_error_%s" % flag
            if hasattr(self, attrname):
                if getattr(self, attrname):
                    text.append("+" + flag)

        return "< ATIOError :: %s >" % " ".join(text)

    def __str__(self):
        return repr(self)
