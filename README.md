# 无人机飞行日志分析器

APM/ArduPilot 固件专用的飞行日志分析工具，支持 .bin, .log, .ulg 格式。

## 功能

- 📊 飞行总览：时长、最大高度、姿态角
- 🛰️ GPS分析：轨迹、速度、定位精度
- 🔋 电池电压：电压曲线、下降率、健康状态
- 📏 高度分析：爬升/下降曲线
- 📳 振动分析：三轴振动 RMS 值
- ⚠️ 异常检测：低电压、超高飞行、大角度姿态
- 📄 HTML报告：一键导出中文分析报告

## 本地运行

```bash
cd dronelog-analyzer
pip install -r requirements.txt
streamlit run mvp/app.py
```

## 在线部署

### 方法：Streamlit Cloud（免费）

1. 将此仓库推送到 GitHub
2. 访问 https://streamlit.io/cloud
3. 登录 GitHub，选择仓库
4. 设置 Main file path 为 `dronelog-analyzer/mvp/app.py`
5. 点击 Deploy

部署完成后，你将获得一个类似 `https://yourname-dronelog-analyzer.streamlit.app` 的网址。

### 方法：Render（免费）

1. 在 `render.yaml` 中配置服务
2. 推送代码到 GitHub
3. 访问 https://render.com 创建服务

## 项目结构

```
dronelog-analyzer/
├── mvp/
│   └── app.py              # Streamlit 前端
├── backend/
│   ├── parsers/            # 日志解析器
│   ├── analyzers/          # 数据分析模块
│   └── report/             # HTML报告生成
├── samples/                # 示例日志
├── tests/                  # 测试
├── requirements.txt        # Python依赖
└── README.md
```