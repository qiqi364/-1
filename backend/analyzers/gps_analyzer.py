"""GPS数据分析"""
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
