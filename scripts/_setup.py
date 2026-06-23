import os

base = r"D:\CODEX运行文件\dronelog-analyzer"

dirs = ["backend", "backend/parsers", "backend/analyzers", "backend/report", "mvp", "tests", "samples", "scripts", "api"]
for d in dirs:
    os.makedirs(os.path.join(base, d), exist_ok=True)

# __init__ files
for d in ["backend", "backend/parsers", "backend/analyzers", "backend/report", "mvp", "tests"]:
    with open(os.path.join(base, d, "__init__.py"), "w") as f:
        f.write("")

# requirements.txt
with open(os.path.join(base, "requirements.txt"), "w", encoding="utf-8") as f:
    f.write("pyulog>=1.12\npymavlink>=2.4.38\npandas>=2.0\nmatplotlib>=3.7\nplotly>=5.18\nstreamlit>=1.30\nnumpy>=1.24\n")

print("Done creating base files")