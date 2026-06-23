"""APM BIN/LOG 文件解析器"""
import struct
from backend.parsers.base import BaseParser

class BinLogParser(BaseParser):
    """解析 APM .bin 和 .log 文件 (MAVLink Binary Log)"""
    
    def parse(self, filepath):
        """解析 BIN/LOG 文件
        
        Returns:
            dict: 包含 attitude, gps, battery, altitude, vibration 等数据
        """
        data = {
            "attitude": [],
            "gps": [],
            "battery": [],
            "altitude": [],
            "vibration": [],
            "rc_channels": [],
            "flight_modes": [],
            "messages": []
        }
        
        with open(filepath, "rb") as f:
            magic = f.read(1)
            if not magic:
                raise ValueError("空文件")
            
            if magic == b"\xfe":
                # MAVLink v1 format
                self._parse_mavlink_v1(f, data)
            elif magic == b"\xd0":
                # BIN v2 format
                self._parse_bin_v2(f, data)
            else:
                # 尝试作为 MAVLink v2 或文本格式
                f.seek(0)
                self._parse_mavlink_v1(f, data)
        
        return data
    
    def _parse_mavlink_v1(self, f, data):
        """解析 MAVLink v1 格式"""
        while True:
            try:
                header = f.read(2)
                if len(header) < 2:
                    break
                msg_len = struct.unpack("B", header[:1])[0]
                msg_id = struct.unpack("B", header[1:2])[0]
                payload = f.read(msg_len)
                if len(payload) < msg_len:
                    break
                f.read(2)  # checksum
                
                self._process_mavlink_msg(msg_id, payload, data)
            except Exception:
                break
    
    def _parse_bin_v2(self, f, data):
        """解析 BIN v2 格式"""
        # Read header
        num_msg_types = struct.unpack("<H", f.read(2))[0]
        for _ in range(num_msg_types):
            msg_type = struct.unpack("<i", f.read(4))[0]
            msg_name_bytes = f.read(6)
            msg_name = msg_name_bytes.decode("ascii", errors="ignore").rstrip("\\x00")
        
        # Parse messages
        while True:
            try:
                header = f.read(14)
                if len(header) < 14:
                    break
                msg_type = struct.unpack("<i", header[:4])[0]
                timestamp_us = struct.unpack("<Q", header[4:12])[0]
                msg_size = struct.unpack("<H", header[12:14])[0]
                payload = f.read(msg_size)
                if len(payload) < msg_size:
                    break
                
                # Convert msg_type to MAVLink ID
                mavlink_id = self._bin_type_to_mavlink(msg_type)
                if mavlink_id is not None:
                    ts_sec = timestamp_us / 1e6
                    self._process_payload(mavlink_id, payload, ts_sec, data)
            except Exception:
                break
    
    def _bin_type_to_mavlink(self, bin_type):
        """BIN v2 type -> MAVLink ID 映射"""
        mapping = {
            -1: 258,   # STATUSTEXT
            -2: 30,    # ATTITUDE
            -3: 31,    # RAW_IMU
            -4: 32,    # SCALED_IMU
            -5: 100,   # LOCATION
            -6: 41,    # GPS_RAW_INT
            -7: 120,   # BATTERY_STATUS
            -8: 125,   # GLOBAL_POSITION_INT
            -9: 140,   # ALTITUDE
            -10: 34,   # RC_CHANNELS
            -11: 177,  # SCALED_PRESSURE
            -12: 231,  # VIBRATION
            -13: 172,  # POWER_BUTTON
            -14: 190,  # GPS2_RAW
            -15: 161,  # NAV_CONTROLLER_OUTPUT
            -16: 174,  # POSITION_TARGET_GLOBAL_INT
            -17: 164,  # SIM_STATE
            -18: 165,  # SIM_SET_STATE
            -19: 166,  # RANGEFINDER
            -20: 167,  # LANDING_TARGET
            -21: 168,  # SERVO_OUTPUT
            -22: 169,  # AHRS
            -23: 170,  # HEROIC
            -24: 171,  # RAW_PRESSURE
            -25: 173,  # LED
            -26: 175,  # MEMORY
            -27: 176,  # VFR_HUD
            -28: 178,  # CYCLE_TIME
            -29: 179,  # FAILSAFE
            -30: 180,  # ACTUATOR_OUTPUT
            -31: 181,  # RADIO
            -32: 182,  # RADIO_CAL
            -33: 183,  # ESC_TELEMETRY
            -34: 184,  # SETPOINT_RAW
            -35: 185,  # LOCAL_POSITION_NED
            -36: 186,  # GLOBAL_POSITION_NED
            -37: 187,  # VISION_POSITION_NED
            -38: 188,  # OPTICAL_FLOW
            -39: 189,  # MAG_CAL_REPORT
            -40: 191,  # GUIDED_LIMITS
        }
        return mapping.get(bin_type)
    
    def _process_mavlink_msg(self, msg_id, payload, data):
        """处理 MAVLink 消息"""
        ts = 0  # 简化：不精确计时
        self._process_payload(msg_id, payload, ts, data)
    
    def _process_payload(self, msg_id, payload, ts, data):
        """根据消息类型处理载荷"""
        view = __import__("struct").pack  # placeholder
        import struct
        
        try:
            if msg_id == 30:  # ATTITUDE
                roll, pitch, yaw = struct.unpack("<fff", payload[:12])
                data["attitude"].append({
                    "time": ts, "roll": roll, "pitch": pitch, "yaw": yaw
                })
            elif msg_id == 41:  # GPS_RAW_INT
                lat, lon = struct.unpack("<ii", payload[:8])
                alt = struct.unpack("<i", payload[8:12])[0]
                data["gps"].append({
                    "time": ts, "lat": lat / 1e7, "lon": lon / 1e7,
                    "alt": alt / 1000 if alt > 0 else 0
                })
            elif msg_id == 120:  # BATTERY_STATUS
                voltage = struct.unpack("<H", payload[:2])[0] / 1000.0
                current = struct.unpack("<h", payload[2:4])[0] / 100.0
                data["battery"].append({
                    "time": ts, "voltage": voltage, "current": current
                })
            elif msg_id == 125:  # GLOBAL_POSITION_INT
                lat, lon = struct.unpack("<ii", payload[:8])
                alt = struct.unpack("<i", payload[8:12])[0] / 1000.0
                data["gps"].append({
                    "time": ts, "lat": lat / 1e7, "lon": lon / 1e7, "alt": alt
                })
            elif msg_id == 140:  # ALTITUDE
                values = struct.unpack("<ffff", payload[:16])
                data["altitude"].append({
                    "time": ts,
                    "actual_alt": values[0],
                    "estimated_alt": values[1],
                    "best_estimate_alt": values[3]
                })
            elif msg_id == 231:  # VIBRATION
                vib = struct.unpack("<fff", payload[:12])
                data["vibration"].append({
                    "time": ts,
                    "vibration_x": vib[0],
                    "vibration_y": vib[1],
                    "vibration_z": vib[2]
                })
            elif msg_id == 34:  # RC_CHANNELS
                if len(payload) >= 18:
                    ch_raw = struct.unpack("<HHHHHHHH", payload[:16])
                    data["rc_channels"].append({
                        "time": ts, "channels": list(ch_raw)
                    })
            elif msg_id == 258:  # STATUSTEXT
                text = payload.rstrip(b"\\x00").decode("utf-8", errors="ignore")
                data["messages"].append({"time": ts, "text": text})
        except Exception:
            pass
    
    def get_supported_formats(self):
        return ["bin", "log"]