"""APM BIN/LOG 文件解析器 - 使用 pymavlink"""
from backend.parsers.base import BaseParser

class BinLogParser(BaseParser):
    """解析 APM .bin 和 .log 文件 (DataFlash BIN log)"""
    
    def parse(self, filepath):
        """解析 BIN/LOG 文件"""
        from pymavlink import DFReader
        import struct
        
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
            f.seek(0)
            
            if magic == b"\xd0":
                log = DFReader.DFReader_binary(filepath, filepath)
            else:
                log = DFReader.DFReader(filepath, filepath)
        
        # 遍历所有消息
        for msg in log:
            mtype = msg.get_type()
            
            if mtype == "ATTITUDE":
                data["attitude"].append({
                    "time": float(msg.time_boot_ms) / 1000.0,
                    "roll": msg.roll,
                    "pitch": msg.pitch,
                    "yaw": msg.yaw
                })
            elif mtype in ("GPS_RAW_INT", "GPS"):
                lat = getattr(msg, "lat", 0)
                lon = getattr(msg, "lon", 0)
                alt = getattr(msg, "alt", 0)
                data["gps"].append({
                    "time": float(msg.time_boot_ms) / 1000.0,
                    "lat": lat / 1e7 if lat else 0,
                    "lon": lon / 1e7 if lon else 0,
                    "alt": alt / 1000.0 if alt and alt != -1 else 0
                })
            elif mtype == "BATTERY":
                data["battery"].append({
                    "time": float(msg.time_boot_ms) / 1000.0,
                    "voltage": msg.voltage_mv / 1000.0 if hasattr(msg, "voltage_mv") else msg.voltage / 1000.0,
                    "current": msg.current_a / 100.0 if hasattr(msg, "current_a") and msg.current_a >= 0 else 0
                })
            elif mtype == "ALTITUDE":
                data["altitude"].append({
                    "time": float(msg.time_boot_ms) / 1000.0,
                    "actual_alt": msg.altitude_monotonic if hasattr(msg, "altitude_monotonic") else 0,
                    "estimated_alt": msg.altitude_local if hasattr(msg, "altitude_local") else 0,
                    "best_estimate_alt": msg.altitude_global if hasattr(msg, "altitude_global") else 0
                })
            elif mtype == "VIBRATION":
                data["vibration"].append({
                    "time": float(msg.time_boot_ms) / 1000.0,
                    "vibration_x": msg.vibration_x,
                    "vibration_y": msg.vibration_y,
                    "vibration_z": msg.vibration_z
                })
            elif mtype == "RC_CHANNELS":
                ch_raw = [
                    getattr(msg, f"chan{i}_raw", 0) for i in range(1, 9)
                ]
                data["rc_channels"].append({
                    "time": float(msg.time_boot_ms) / 1000.0,
                    "channels": ch_raw
                })
            elif mtype == "STATUSTEXT":
                text = getattr(msg, "text", "").rstrip("\\x00").decode("utf-8", errors="ignore")
                data["messages"].append({
                    "time": float(msg.time_boot_ms) / 1000.0,
                    "text": text
                })
            elif mtype == "NAV_CONTROLLER_OUTPUT":
                data["flight_modes"].append({
                    "time": float(msg.time_boot_ms) / 1000.0,
                    "nav_roll": msg.nav_roll,
                    "nav_pitch": msg.nav_pitch,
                    "nav_bearing": msg.nav_bearing,
                    "target_bearing": msg.target_bearing,
                    "wp_dist": msg.wp_dist
                })
        
        return data
    
    def get_supported_formats(self):
        return ["bin", "log"]