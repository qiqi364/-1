"""高度数据分析"""
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
