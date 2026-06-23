import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backend.parsers.factory import create_parser, supported_formats
from backend.analyzers import flight_overview, gps_analyzer, voltage_analyzer, altitude_analyzer, vibration_analyzer, anomaly_detector
from backend.report.report_generator import generate_html

st.set_page_config(
    page_title="无人机飞行日志分析器",
    page_icon="🚁",
    layout="wide"
)

st.title("🚁 无人机飞行日志分析器")
st.caption("APM / ArduPilot 固件专用 | 支持 .bin, .log, .ulg 格式")

# --- 文件上传 ---
col1, col2 = st.columns([3, 1])
with col1:
    uploaded = st.file_uploader(
        "选择飞行日志文件",
        type=["bin", "log", "ulg"],
        label_visibility="collapsed"
    )
with col2:
    st.caption(f"支持格式: {', '.join(supported_formats())}")

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "samples")
sample_files = []
if os.path.isdir(SAMPLE_DIR):
    for ext in supported_formats():
        import glob
        sample_files.extend(sorted(glob.glob(os.path.join(SAMPLE_DIR, "*" + ext))))

sample_paths = {os.path.basename(p): p for p in sample_files}

if sample_paths:
    with st.expander("或试用示例日志", expanded=False):
        sel = st.selectbox("选择示例", ["-- 请选择 --"] + list(sample_paths.keys()))
        if sel != "-- 请选择 --":
            uploaded = sel
            st.info(f"已选择: {sel}")

if uploaded:
    # 保存上传的文件到临时位置
    with st.spinner("正在解析飞行日志..."):
        try:
            if isinstance(uploaded, str):
                filepath = uploaded
                filename = os.path.basename(filepath)
            else:
                ext = uploaded.name.split(".")[-1].lower()
                filepath = os.path.join("/tmp", f"upload_{uploaded.name}")
                with open(filepath, "wb") as f:
                    f.write(uploaded.read())
                filename = uploaded.name
            
            # 创建解析器并解析
            parser = create_parser(ext)
            parsed_data = parser.parse(filepath)
            
            st.success(f"✅ 成功解析 {filename}！")
            
            # --- 运行所有分析器 ---
            overview = flight_overview.analyze(parsed_data)
            gps_res = gps_analyzer.analyze(parsed_data)
            voltage_res = voltage_analyzer.analyze(parsed_data)
            altitude_res = altitude_analyzer.analyze(parsed_data)
            vibration_res = vibration_analyzer.analyze(parsed_data)
            anomaly_res = anomaly_detector.analyze(parsed_data)
            
            # --- 统计卡片 ---
            st.subheader("📊 飞行统计")
            kpi_cols = st.columns(5)
            kpi_cols[0].metric("飞行时长", f"{overview.get('duration', 0)} 秒")
            kpi_cols[1].metric("最大高度", f"{overview.get('max_altitude', 0)} 米")
            kpi_cols[2].metric("最大滚转角", f"{overview.get('max_roll', 0)}°")
            kpi_cols[3].metric("最低电压", f"{overview.get('min_voltage', 0)} V")
            kpi_cols[4].metric("飞行状态", overview.get("flight_status", "未知"))
            
            # --- Tab 页 ---
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "飞行总览", "GPS轨迹", "电池电压", "高度变化", "振动分析", "异常检测"
            ])
            
            with tab1:
                st.subheader("姿态数据")
                attitude = parsed_data.get("attitude", [])
                if attitude:
                    att_df = pd.DataFrame(attitude)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=att_df["time"], y=att_df["roll"], name="滚转(°)", line=dict(color="#e53935")))
                    fig.add_trace(go.Scatter(x=att_df["time"], y=att_df["pitch"], name="俯仰(°)", line=dict(color="#1a73e8")))
                    fig.add_trace(go.Scatter(x=att_df["time"], y=att_df["yaw"], name="偏航(°)", line=dict(color="#43A047")))
                    fig.update_layout(xaxis_title="时间(秒)", yaxis_title="角度(度)", template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(att_df.head(20), use_container_width=True)
                else:
                    st.warning("未检测到姿态数据")
            
            with tab2:
                st.subheader("GPS数据")
                gps = parsed_data.get("gps", [])
                if gps:
                    gps_df = pd.DataFrame(gps)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=gps_df["time"], y=gps_df["lat"], name="纬度", line=dict(color="#1a73e8")))
                    fig.add_trace(go.Scatter(x=gps_df["time"], y=gps_df["lon"], name="经度", line=dict(color="#e53935")))
                    fig.update_layout(xaxis_title="时间(秒)", yaxis_title="坐标", template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.metric("GPS数据点数", len(gps))
                    st.metric("最大水平距离", f"{gps_res.get('max_horizontal_distance', 0)} 米")
                else:
                    st.warning("未检测到GPS数据")
            
            with tab3:
                st.subheader("电池电压")
                batt = parsed_data.get("battery", [])
                if batt:
                    batt_df = pd.DataFrame(batt)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=batt_df["time"], y=batt_df["voltage"], name="电压(V)", line=dict(color="#FF9800"), fill="tozeroy"))
                    fig.update_layout(xaxis_title="时间(秒)", yaxis_title="电压(V)", template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.metric("最低电压", f"{voltage_res.get('min_voltage', 0)} V")
                    st.metric("电压下降", f"{voltage_res.get('voltage_drop', 0)} V")
                    st.metric("状态", voltage_res.get("status", "未知"))
                else:
                    st.warning("未检测到电压数据")
            
            with tab4:
                st.subheader("高度数据")
                if "altitude" in parsed_data and parsed_data["altitude"]:
                    alt_df = pd.DataFrame(parsed_data["altitude"])
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=alt_df["time"], y=alt_df.get("best_estimate_alt", alt_df.get("actual_alt", 0)), name="高度(m)", line=dict(color="#9C27B0"), fill="tozeroy"))
                    fig.update_layout(xaxis_title="时间(秒)", yaxis_title="高度(米)", template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                elif gps:
                    gps_df = pd.DataFrame(gps)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=gps_df["time"], y=gps_df["alt"], name="高度(m)", line=dict(color="#9C27B0"), fill="tozeroy"))
                    fig.update_layout(xaxis_title="时间(秒)", yaxis_title="高度(米)", template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("未检测到高度数据")
                st.metric("最大高度", f"{altitude_res.get('max_altitude', 0)} 米")
                st.metric("高度范围", f"{altitude_res.get('altitude_range', 0)} 米")
            
            with tab5:
                st.subheader("振动数据")
                vib = parsed_data.get("vibration", [])
                if vib:
                    vib_df = pd.DataFrame(vib)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=vib_df["time"], y=vib_df["vibration_x"], name="X轴", line=dict(color="#e53935")))
                    fig.add_trace(go.Scatter(x=vib_df["time"], y=vib_df["vibration_y"], name="Y轴", line=dict(color="#1a73e8")))
                    fig.add_trace(go.Scatter(x=vib_df["time"], y=vib_df["vibration_z"], name="Z轴", line=dict(color="#43A047")))
                    fig.update_layout(xaxis_title="时间(秒)", yaxis_title="振动(g)", template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.metric("RMS总值", vibration_res.get("rms_total", 0))
                    st.metric("严重程度", vibration_res.get("severity", "未知"))
                else:
                    st.warning("未检测到振动数据")
            
            with tab6:
                st.subheader("异常检测结果")
                st.metric("异常总数", anomaly_res.get("total_anomalies", 0))
                st.metric("高风险", anomaly_res.get("high_severity", 0))
                st.metric("中风险", anomaly_res.get("medium_severity", 0))
                
                if anomaly_res.get("anomalies"):
                    anom_df = pd.DataFrame(anomaly_res["anomalies"])
                    st.dataframe(anom_df, use_container_width=True)
                else:
                    st.success("✅ 未检测到异常！飞行数据良好。")
            
            # --- 导出报告 ---
            st.divider()
            if st.button("📄 导出HTML报告"):
                html_report = generate_html(overview, gps_res, voltage_res, altitude_res, vibration_res, anomaly_res, attitude_data=parsed_data.get("attitude", []))
                
                import base64
                b64 = base64.b64encode(html_report.encode("utf-8")).decode()
                href = f'data:text/html;charset=utf-8;base64,{b64}'
                st.markdown(f'<a href="{href}" download="{os.path.splitext(filename)[0]}_分析报告.html" style="color:#1a73e8;font-weight:bold;">⬇️ 点击下载分析报告</a>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ 解析失败: {str(e)}")
            import traceback
            st.code(traceback.format_exc())