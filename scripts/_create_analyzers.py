import os

base = r"D:\CODEX运行文件\dronelog-analyzer\backend"

# flight_overview.py
with open(os.path.join(base, "analyzers", "flight_overview.py"), "w", encoding="utf-8") as f:
    f.write('''"""飞行总览分析"""
def analyze(data):
    """生成飞行总览数据"""
    attitude = data.get("attitude", [])
    gps = data.get("gps", [])
    battery = data.get("battery", [])
    
    duration = 0
    max_roll = 0
    max_pitch = 0
    
    if attitude:
        duration = attitude[-1]["time"] - attitude[0]["time"] if len(attitude) > 1 else 0
        max_roll = max(abs(a["roll"]) for a in attitude)
        max_pitch = max(abs(a["pitch"]) for a in attitude)
    
    max_alt = max((g["alt"] for g in gps), default=0)
    min_voltage = min((b["voltage"] for b in battery), default=0)
    
    return {
        "duration": round(duration, 1),
        "max_roll": round(max_roll, 1),
        "max_pitch": round(max_pitch, 1),
        "max_altitude": round(max_alt, 1),
        "min_voltage": round(min_voltage, 2),
        "total_attitude_samples": len(attitude),
        "total_gps_samples": len(gps),
        "total_battery_samples": len(battery),
        "flight_status": "正常" if min_voltage > 3.3 and max_alt < 500 else "注意"
    }
''')
print("Created flight_overview.py")

# gps_analyzer.py
with open(os.path.join(base, "analyzers", "gps_analyzer.py"), "w", encoding="utf-8") as f:
    f.write('''"""GPS数据分析"""
def analyze(data):
    """分析GPS数据"""
    import math
    gps = data.get("gps", [])
    if not gps:
        return {"error": "无GPS数据"}
    
    lats = [g["lat"] for g in gps]
    lons = [g["lon"] for g in gps]
    alts = [g["alt"] for g in gps]
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    max_dist = 0
    for i in range(1, len(gps)):
        d = haversine(gps[i-1]["lat"], gps[i-1]["lon"], gps[i]["lat"], gps[i]["lon"])
        max_dist = max(max_dist, d)
    
    speeds = []
    for i in range(1, len(gps)):
        dt = gps[i]["time"] - gps[i-1]["time"]
        if dt > 0:
            speeds.append(max_dist / dt)
    
    return {
        "sample_count": len(gps),
        "start_lat": round(gps[0]["lat"], 6),
        "start_lon": round(gps[0]["lon"], 6),
        "end_lat": round(gps[-1]["lat"], 6),
        "end_lon": round(gps[-1]["lon"], 6),
        "max_altitude": round(max(alts), 1),
        "min_altitude": round(min(alts), 1),
        "max_horizontal_distance": round(max_dist, 1),
        "avg_speed": round(sum(speeds)/len(speeds), 1) if speeds else 0,
        "max_speed": round(max(speeds), 1) if speeds else 0,
    }
''')
print("Created gps_analyzer.py")

# voltage_analyzer.py
with open(os.path.join(base, "analyzers", "voltage_analyzer.py"), "w", encoding="utf-8") as f:
    f.write('''"""电压数据分析"""
def analyze(data):
    """分析电池电压数据"""
    battery = data.get("battery", [])
    if not battery:
        return {"error": "无电压数据"}
    
    voltages = [b["voltage"] for b in battery]
    currents = [b["current"] for b in battery if b.get("current") is not None]
    
    min_v = min(voltages)
    max_v = max(voltages)
    avg_v = sum(voltages) / len(voltages)
    
    return {
        "sample_count": len(battery),
        "min_voltage": round(min_v, 2),
        "max_voltage": round(max_v, 2),
        "avg_voltage": round(avg_v, 2),
        "voltage_drop": round(max_v - min_v, 2),
        "avg_current": round(sum(currents)/len(currents), 1) if currents else 0,
        "status": "正常" if min_v > 3.3 else "低电压警告"
    }
''')
print("Created voltage_analyzer.py")

# altitude_analyzer.py
with open(os.path.join(base, "analyzers", "altitude_analyzer.py"), "w", encoding="utf-8") as f:
    f.write('''"""高度数据分析"""
def analyze(data):
    """分析高度数据"""
    altitude = data.get("altitude", [])
    gps = data.get("gps", [])
    
    sources = altitude if altitude else gps
    if not sources:
        return {"error": "无高度数据"}
    
    alts = []
    for s in sources:
        a = s.get("alt", s.get("best_estimate_alt", s.get("actual_alt", 0)))
        alts.append(a)
    
    return {
        "sample_count": len(sources),
        "max_altitude": round(max(alts), 1),
        "min_altitude": round(min(alts), 1),
        "avg_altitude": round(sum(alts)/len(alts), 1),
        "altitude_range": round(max(alts) - min(alts), 1)
    }
''')
print("Created altitude_analyzer.py")

# vibration_analyzer.py
with open(os.path.join(base, "analyzers", "vibration_analyzer.py"), "w", encoding="utf-8") as f:
    f.write('''"""振动数据分析"""
def analyze(data):
    """分析振动数据"""
    import math
    vib = data.get("vibration", [])
    if not vib:
        return {"error": "无振动数据"}
    
    vx = [v["vibration_x"] for v in vib]
    vy = [v["vibration_y"] for v in vib]
    vz = [v["vibration_z"] for v in vib]
    
    total_rms = math.sqrt(
        sum(v**2 for v in vx) / len(vx) +
        sum(v**2 for v in vy) / len(vy) +
        sum(v**2 for v in vz) / len(vz)
    ) / math.sqrt(3) if vx and vy and vz else 0
    
    severity = "轻微" if total_rms < 1 else ("中等" if total_rms < 5 else "严重")
    
    return {
        "sample_count": len(vib),
        "rms_total": round(total_rms, 2),
        "max_x": round(max(abs(v) for v in vx), 2),
        "max_y": round(max(abs(v) for v in vy), 2),
        "max_z": round(max(abs(v) for v in vz), 2),
        "severity": severity
    }
''')
print("Created vibration_analyzer.py")

# anomaly_detector.py
with open(os.path.join(base, "analyzers", "anomaly_detector.py"), "w", encoding="utf-8") as f:
    f.write('''"""异常检测"""
def analyze(data):
    """检测飞行异常"""
    anomalies = []
    
    battery = data.get("battery", [])
    for b in battery:
        if b["voltage"] < 3.3:
            anomalies.append({
                "type": "低电压",
                "severity": "高",
                "time": b["time"],
                "value": b["voltage"],
                "message": f"电池电压过低: {b['voltage']:.2f}V"
            })
    
    gps = data.get("gps", [])
    for g in gps:
        if g.get("alt", 0) > 120:
            anomalies.append({
                "type": "超高飞行",
                "severity": "中",
                "time": g["time"],
                "value": g["alt"],
                "message": f"飞行高度超过120米限制: {g['alt']:.1f}m"
            })
    
    attitude = data.get("attitude", [])
    for a in attitude:
        if abs(a["roll"]) > 45 or abs(a["pitch"]) > 45:
            anomalies.append({
                "type": "大角度姿态",
                "severity": "中",
                "time": a["time"],
                "value": max(abs(a["roll"]), abs(a["pitch"])),
                "message": f"姿态角过大: 滚转{a['roll']:.1f}, 俯仰{a['pitch']:.1f}"
            })
    
    return {
        "total_anomalies": len(anomalies),
        "high_severity": len([a for a in anomalies if a["severity"] == "高"]),
        "medium_severity": len([a for a in anomalies if a["severity"] == "中"]),
        "anomalies": anomalies[:50]
    }
''')
print("Created anomaly_detector.py")

print("All analyzer modules created!")