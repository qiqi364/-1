"""HTML报告生成器"""
import os
from datetime import datetime

def generate_html(summary, gps_data, voltage_data, altitude_data, vibration_data, anomaly_data, attitude_data):
    """生成中文HTML分析报告"""
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>飞行日志分析报告</title>
<style>
body {{ font-family: "Microsoft YaHei", sans-serif; margin: 20px; background: #f5f7fa; }}
h1 {{ color: #1a73e8; border-bottom: 3px solid #1a73e8; padding-bottom: 10px; }}
h2 {{ color: #333; margin-top: 30px; border-left: 4px solid #1a73e8; padding-left: 12px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #1a73e8; color: white; }}
tr:nth-child(even) {{ background: #f8f9fa; }}
.alert-high {{ background: #ffebee !important; color: #c62828; font-weight: bold; }}
.alert-medium {{ background: #fff3e0 !important; }}
.card {{ background: white; border-radius: 8px; padding: 16px; margin: 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.footer {{ text-align: center; color: #999; margin-top: 40px; padding: 20px; font-size: 12px; }}
</style>
</head>
<body>
<h1>无人机飞行日志分析报告</h1>
<p>生成时间: {now}</p>

<h2>一、飞行总览</h2>
<div class="card">
<table>
<tr><th>指标</th><th>数值</th></tr>
<tr><td>飞行时长</td><td>{summary.get("duration", 0)} 秒</td></tr>
<tr><td>最大滚转角</td><td>{summary.get("max_roll", 0)} 度</td></tr>
<tr><td>最大俯仰角</td><td>{summary.get("max_pitch", 0)} 度</td></tr>
<tr><td>最大高度</td><td>{summary.get("max_altitude", 0)} 米</td></tr>
<tr><td>最低电压</td><td>{summary.get("min_voltage", 0)} V</td></tr>
<tr><td>飞行状态</td><td>{summary.get("flight_status", "未知")}</td></tr>
<tr><td>姿态数据点数</td><td>{summary.get("total_attitude_samples", 0)}</td></tr>
<tr><td>GPS数据点数</td><td>{summary.get("total_gps_samples", 0)}</td></tr>
<tr><td>电压数据点数</td><td>{summary.get("total_battery_samples", 0)}</td></tr>
</table>
</div>

<h2>二、GPS分析</h2>
<div class="card">
<table>
<tr><th>指标</th><th>数值</th></tr>
<tr><td>起始纬度</td><td>{gps_data.get("start_lat", "N/A")}</td></tr>
<tr><td>起始经度</td><td>{gps_data.get("start_lon", "N/A")}</td></tr>
<tr><td>结束纬度</td><td>{gps_data.get("end_lat", "N/A")}</td></tr>
<tr><td>结束经度</td><td>{gps_data.get("end_lon", "N/A")}</td></tr>
<tr><td>最大水平距离</td><td>{gps_data.get("max_horizontal_distance", 0)} 米</td></tr>
<tr><td>最大高度</td><td>{gps_data.get("max_altitude", 0)} 米</td></tr>
<tr><td>平均速度</td><td>{gps_data.get("avg_speed", 0)} m/s</td></tr>
</table>
</div>

<h2>三、电池电压分析</h2>
<div class="card">
<table>
<tr><th>指标</th><th>数值</th></tr>
<tr><td>最低电压</td><td>{voltage_data.get("min_voltage", "N/A")} V</td></tr>
<tr><td>最高电压</td><td>{voltage_data.get("max_voltage", "N/A")} V</td></tr>
<tr><td>平均电压</td><td>{voltage_data.get("avg_voltage", "N/A")} V</td></tr>
<tr><td>电压下降</td><td>{voltage_data.get("voltage_drop", 0)} V</td></tr>
<tr><td>平均电流</td><td>{voltage_data.get("avg_current", 0)} A</td></tr>
<tr><td>状态</td><td>{voltage_data.get("status", "未知")}</td></tr>
</table>
</div>

<h2>四、振动分析</h2>
<div class="card">
<table>
<tr><th>指标</th><th>数值</th></tr>
<tr><td>RMS总值</td><td>{vibration_data.get("rms_total", 0)}</td></tr>
<tr><td>X轴最大值</td><td>{vibration_data.get("max_x", 0)}</td></tr>
<tr><td>Y轴最大值</td><td>{vibration_data.get("max_y", 0)}</td></tr>
<tr><td>Z轴最大值</td><td>{vibration_data.get("max_z", 0)}</td></tr>
<tr><td>严重程度</td><td>{vibration_data.get("severity", "未知")}</td></tr>
</table>
</div>

<h2>五、异常检测</h2>
<div class="card">
<p>共发现 <strong>{anomaly_data.get("total_anomalies", 0)}</strong> 条异常</p>
<p>高风险: {anomaly_data.get("high_severity", 0)} | 中风险: {anomaly_data.get("medium_severity", 0)}</p>
<table>
<tr><th>时间(秒)</th><th>类型</th><th>严重程度</th><th>详情</th></tr>
"""
    
    for a in anomaly_data.get("anomalies", [])[:20]:
        cls = "alert-high" if a["severity"] == "高" else "alert-medium"
        html += f'<tr class="{cls}"><td>{a["time"]:.1f}</td><td>{a["type"]}</td><td>{a["severity"]}</td><td>{a["message"]}</td></tr>\n'
    
    html += """</table>
</div>

<div class="footer">
<p>由无人机飞行日志分析器自动生成 | APM固件测试工具</p>
</div>
</body>
</html>"""
    
    return html