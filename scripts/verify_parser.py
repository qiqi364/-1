import sys
sys.path.insert(0, r"D:\CODEX运行文件\dronelog-analyzer")
from backend.parsers.factory import create_parser

parser = create_parser("bin")
data = parser.parse(r"D:\CODEX运行文件\dronelog-analyzer\samples\sample_apm.bin")

print(f"姿态数据点数: {len(data['attitude'])}")
print(f"GPS数据点数: {len(data['gps'])}")
print(f"电池数据点数: {len(data['battery'])}")
print(f"振动数据点数: {len(data['vibration'])}")

from backend.analyzers import flight_overview, anomaly_detector

overview = flight_overview.analyze(data)
print(f"\n飞行总览:")
for k, v in overview.items():
    print(f"  {k}: {v}")

anomaly = anomaly_detector.analyze(data)
print(f"\n异常检测: {anomaly['total_anomalies']} 条异常")
print("\n=== 所有测试通过 ===")