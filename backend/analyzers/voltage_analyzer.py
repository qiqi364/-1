"""电压数据分析"""
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
