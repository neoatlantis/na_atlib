#!/usr/bin/env python3

from smbus2 import SMBus, i2c_msg
import time


class I2CBus:
    def __init__(self, bus_num, addr, wake_method="i2c", twhi_ms=2.5):
        self.bus = SMBus(bus_num)
        self.addr = addr
        self.wake_method = wake_method
        self.twhi = twhi_ms / 1000.0          # 唤醒脉冲后到可通信前的等待时间
        self._pi = None
        if wake_method == "gpio":
            import pigpio
            self._pi = pigpio.pi()
            if not self._pi.connected:
                raise RuntimeError("pigpio 守护进程没运行: sudo pigpiod")

    def write(self, data):
        return self.bus.i2c_rdwr(i2c_msg.write(self.addr, list(data)))

    def read(self, n, rstrip=False):
        msg = i2c_msg.read(self.addr, n)
        self.bus.i2c_rdwr(msg)
        msg = bytes(msg)
        if rstrip:
            msg = msg.rstrip(b'\xff')
        return msg

    def wake(self):
        if self.wake_method == "gpio":
            self._wake_gpio()
        else:
            self._wake_i2c()
        time.sleep(self.twhi)

    def _wake_i2c(self):
        """
        通过向地址 0x00 写一个 0x00 字节, 让 SDA 在整个地址字节期间保持低电平,
        从而产生唤醒脉冲 (tWLO, 最小约 60us)。
        ⚠ 这要求 I2C 时钟 <= ~125kHz。树莓派默认 100kHz 时一个字节约 80us, 正好够。
          如果你把总线提到 400kHz, 这个方法会失败 —— 改用 --wake gpio。
        设备(以及地址 0x00)不会 ACK, 抛 OSError 属正常, 忽略即可。
        """
        try:
            self.bus.i2c_rdwr(i2c_msg.write(0x00, [0x00]))
        except OSError:
            pass
        time.sleep(0.01)

    def _wake_gpio(self):
        """直接把 SDA(GPIO2) 拉低 ~0.1ms 再交还给 I2C。与总线时钟无关, 更稳。"""
        import pigpio
        SDA = 2
        self._pi.set_mode(SDA, pigpio.OUTPUT)
        self._pi.write(SDA, 0)
        time.sleep(0.0001)               # >=60us; 偏长也无害
        self._pi.set_mode(SDA, pigpio.ALT0)   # 交还给硬件 I2C, 上拉电阻把 SDA 拉高

    def close(self):
        try:
            self.bus.close()
        except Exception:
            pass
        if self._pi:
            self._pi.stop()

    def __enter__(self, *args, **argv):
        return self

    def __exit__(self, *args, **argv):
        self.close()

