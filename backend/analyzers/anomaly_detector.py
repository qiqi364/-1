"""异常检测"""
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
