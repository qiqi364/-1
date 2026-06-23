"""飞行总览分析"""
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
