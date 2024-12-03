import os
import sys

# 添加项目根目录到 PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 运行 Streamlit 应用
os.system(f"streamlit run {os.path.join('stream', 'demo.py')}") 