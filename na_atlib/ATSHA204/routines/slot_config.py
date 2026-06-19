#!/usr/bin/env python3

class SlotConfig:

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        yn = lambda x: "✅" if x else "❌"
        return "< SlotConfig ReadKey=%2d WriteKey=%2d CheckOnly:%2s LimitedUse:%2s EncryptRead:%2s IsSecret:%2s %s\t%s >" % (
            self.read_key,
            self.write_key,
            yn(self.check_only),
            yn(self.limited_use),
            yn(self.encrypt_read),
            yn(self.is_secret),
            "No_DeriveKey" if not self.derive_key_allowed else (
                "DeriveKey_From_" + (
                    "Parent" if self.derive_key_by_creation \
                    else "Self"
                ) + " " + (
                    "DeriveKey_Must_Auth" if self.derive_key_auth_required\
                    else "DeriveKey_No_Auth"
                )
            ),
            "No_Write" if not self.write_key_allowed else (
                "Write_Cleartext" if not self.write_key_must_encrypt else\
                "Write_Must_Encrypt"
            )
        )

    @property
    def read_key(self):
        return self.value & 0x0F

    @property
    def check_only(self):
        return bool(self.value & (1<<4))

    @property
    def limited_use(self):
        return bool(self.value & (1<<5))


    @property
    def encrypt_read(self):
        return bool(self.value & (1<<6))
    
    @property
    def is_secret(self):
        return bool(self.value & (1<<7))

    @property
    def write_key(self):
        return (self.value >> 8) & 0x0F


    @property
    def derive_key_allowed(self):
        return bool(self.value & (1<<13))

    @property
    def derive_key_auth_required(self):
        return bool(self.value & (1<<15))

    @property
    def derive_key_by_creation(self):
        return bool(self.value & (1<<12))


    @property
    def write_key_allowed(self):
        bit13 = bool(self.value & (1<<13))
        bit14 = bool(self.value & (1<<14))
        bit15 = bool(self.value & (1<<15))
        return not bool(
            ((not bit14) and bit13) or
            ((not bit14) and bit15)
        )

    @property
    def write_key_must_encrypt(self):
        return bool(self.value & (1<<14))