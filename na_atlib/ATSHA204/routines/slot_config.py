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

    def __bytes__(self):
        return bytes([self.value & 0xFF, (self.value & 0xFF00)>>8])

    def __set_value(self, mask, value):
        # e.g. mask = 0x0F, set last 4 bits from value
        self.value = (self.value & (0xFFFF ^ mask)) | (value & mask)


    @property
    def read_key(self): return self.value & 0x0F

    @read_key.setter
    def read_key(self, v): self.__set_value(0x0F, v)


    @property
    def check_only(self): return bool(self.value & (1<<4))

    @check_only.setter
    def check_only(self, v): self.__set_value(1<<4, v << 4)


    @property
    def limited_use(self): return bool(self.value & (1<<5))

    @limited_use.setter
    def limited_use(self, v): self.__set_value(1<<5, v << 5)


    @property
    def encrypt_read(self): return bool(self.value & (1<<6))

    @encrypt_read.setter
    def encrypt_read(self, v): self.__set_value(1<<6, v << 6)

    
    @property
    def is_secret(self): return bool(self.value & (1<<7))

    @is_secret.setter
    def is_secret(self, v): self.__set_value(1<<7, v << 7)


    @property
    def write_key(self): return (self.value >> 8) & 0x0F

    @write_key.setter
    def write_key(self, v): self.__set_value(0x0F00, v << 8)


    @property
    def derive_key_allowed(self): return bool(self.value & (1<<13))

    @derive_key_allowed.setter
    def derive_key_allowed(self, v): self.__set_value(1<<13, v << 13)


    @property
    def derive_key_auth_required(self):
        return bool(self.value & (1<<15))

    @derive_key_auth_required.setter
    def derive_key_auth_required(self, v): self.__set_value(1<<15, v<<15)


    @property
    def derive_key_by_creation(self): return bool(self.value & (1<<12))

    @derive_key_by_creation.setter
    def derive_key_by_creation(self, v): self.__set_value(1<<12, v<<12)


    @property
    def write_key_must_encrypt(self): return bool(self.value & (1<<14))

    @write_key_must_encrypt.setter
    def write_key_must_encrypt(self, v): self.__set_value(1<<14, v<<14)


    @property
    def write_key_allowed(self):
        bit13 = bool(self.value & (1<<13))
        bit14 = bool(self.value & (1<<14))
        bit15 = bool(self.value & (1<<15))
        return not bool(
            ((not bit14) and bit13) or
            ((not bit14) and bit15)
        )

    