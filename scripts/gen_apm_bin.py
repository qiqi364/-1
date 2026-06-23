import struct
import math
import random
import os

filepath = r"D:\CODEX运行文件\dronelog-analyzer\samples\sample_apm.bin"
os.makedirs(os.path.dirname(filepath), exist_ok=True)

types = [
    (-2, "ATTITUDE", 18),
    (-3, "RAW_IMU", 24),
    (-6, "GPS_RAW_INT", 28),
    (-7, "BATTERY_STATUS", 14),
    (-8, "GLOBAL_POSITION_INT", 28),
    (-9, "ALTITUDE", 16),
    (-10, "RC_CHANNELS", 18),
    (-12, "VIBRATION", 12),
    (-25, "STATUSTEXT", 50),
]

with open(filepath, "wb") as f:
    f.write(b"\xd0")
    f.write(struct.pack("<H", len(types)))
    
    for bin_type, name, size in types:
        f.write(struct.pack("<i", bin_type))
        f.write(name.encode("ascii")[:6].ljust(6, b"\x00"))
        f.write(struct.pack("B", size))
    
    for i in range(600):
        t = i * 0.1
        ts_us = int(t * 1e6)
        
        # ATTITUDE (idx 0, size 18) - 3 floats + 2 bytes padding
        roll = 5 * math.sin(t * 0.5)
        pitch = 3 * math.sin(t * 0.3)
        yaw = t * 2 % 360 - 180
        f.write(struct.pack("<i", 0))
        f.write(struct.pack("<Q", ts_us))
        f.write(struct.pack("<fff", roll, pitch, yaw))
        f.write(b"\x00\x00")  # padding to 18 bytes
        
        # GPS GLOBAL_POSITION_INT (idx 4, size 28) every 10
        if i % 10 == 0:
            lat = 39.9042 + t * 0.00001
            lon = 116.4074 + t * 0.00002
            alt = 50 + 20 * math.sin(t * 0.1)
            f.write(struct.pack("<i", 4))
            f.write(struct.pack("<Q", ts_us))
            f.write(struct.pack("<iii", int(lat * 1e7), int(lon * 1e7), int(alt * 1000)))
            f.write(b"\x00" * 16)  # padding to 28 bytes
        
        # Battery (idx 3, size 14) every 5
        if i % 5 == 0:
            voltage = 12.6 - t * 0.01
            current = 10 + 5 * math.sin(t * 0.2)
            f.write(struct.pack("<i", 3))
            f.write(struct.pack("<Q", ts_us))
            f.write(struct.pack("<HHhI", int(voltage * 1000), int(current * 100), 0, int(t * 1000)))
        
        # Vibration (idx 7, size 12) every 2
        if i % 2 == 0:
            vib_x = 0.1 * random.random()
            vib_y = 0.15 * random.random()
            vib_z = 0.2 * random.random()
            f.write(struct.pack("<i", 7))
            f.write(struct.pack("<Q", ts_us))
            f.write(struct.pack("<fff", vib_x, vib_y, vib_z))

print(f"Generated {filepath}")
print(f"File size: {os.path.getsize(filepath)} bytes")