"""振动数据分析"""
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
