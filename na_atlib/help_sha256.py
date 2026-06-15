#!/usr/bin/env python3

# authored by Claude

def sha256_pad(message: bytes) -> bytes:
    """
    按 RFC 4634 / RFC 6234 第 4.1 节的方案对任意 bytes 输入做 SHA-256 填充。
    返回长度始终是 64 字节（512 比特）的整数倍，可直接切分成 512 比特块处理。
    """
    bit_len = len(message) * 8  # 原始消息比特长度
    if bit_len >= 1 << 64:
        raise ValueError("消息过长，SHA-256 最多支持 2**64 - 1 比特")

    # 1. 追加单个 '1' 比特，写成字节即 0x80
    padded = message + b"\x80"

    # 2. 追加 '0' 字节，使长度对 64 取模等于 56（为后面 8 字节长度域留位）
    pad_len = (56 - len(padded)) % 64
    padded += b"\x00" * pad_len

    # 3. 追加 64 比特大端表示的原始比特长度
    padded += bit_len.to_bytes(8, byteorder="big")

    return padded