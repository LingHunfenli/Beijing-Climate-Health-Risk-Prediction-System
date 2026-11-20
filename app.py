"""
智能体可视化平台 — 主入口
北京市气候健康风险预警全流程自动化分析系统
"""

import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="北京气候健康风险预警平台",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 将项目根目录加入path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# ============================================================
# 侧边栏 — 全局配置
# ============================================================
st.sidebar.title("🏥 气候健康风险预警平台")
st.sidebar.markdown("---")

st.sidebar.header("📋 分析配置")

# 目标行政区
all_districts = [
    "顺义", "海淀", "延庆", "密云", "怀柔", "平谷", "通州",
    "朝阳", "昌平", "门头沟", "石景山", "丰台", "大兴", "房山", "北京",
]
selected_districts = st.sidebar.multiselect(
    "目标行政区", all_districts,
    default=["海淀", "朝阳", "北京"],
    help="选择需要分析的目标行政区"
)

# 时间范围
col1, col2 = st.sidebar.columns(2)
with col1:
    start_year = st.number_input("起始年", 2015, 2026, 2020)
with col2:
    end_year = st.number_input("结束年", 2015, 2026, 2026)

st.sidebar.markdown("---")

# 一键启动
if st.sidebar.button("🚀 一键启动全流程分析", type="primary", use_container_width=True):
    st.sidebar.success("管道已启动！请在各页面查看进度。")
    st.session_state.pipeline_started = True
    st.session_state.config = {
        "districts": selected_districts,
        "start_year": start_year,
        "end_year": end_year,
    }

# 数据状态
st.sidebar.markdown("---")
st.sidebar.header("📊 数据状态")

weather_path = os.path.join(PROJECT_ROOT, "output", "weather_standard.csv")
disease_path = os.path.join(PROJECT_ROOT, "output", "disease_standard.csv")
model_path = os.path.join(PROJECT_ROOT, "models", "model_ranking.json")

if os.path.exists(weather_path):
    st.sidebar.success(f"✅ 气象数据就绪")
else:
    st.sidebar.error("❌ 气象数据未就绪")

if os.path.exists(disease_path):
    try:
        dd = pd.read_csv(disease_path, encoding="utf-8-sig")
        if len(dd) > 0:
            st.sidebar.success(f"✅ 疾病数据就绪 ({len(dd)}行)")
        else:
            st.sidebar.warning("⚠️ 疾病数据为空（模板已就绪）")
    except Exception:
        st.sidebar.warning("⚠️ 疾病数据待上传")
else:
    st.sidebar.warning("⚠️ 疾病数据待上传")

if os.path.exists(model_path):
    st.sidebar.success("✅ 模型产物就绪")
else:
    st.sidebar.info("📌 模型待训练")

# AI 助手配置
st.sidebar.markdown("---")
st.sidebar.header("🤖 AI 助手")

from agent.llm_assistant import PROVIDER_PRESETS

# 初始化 session_state
if "llm_api_key" not in st.session_state:
    st.session_state.llm_api_key = ""
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "deepseek"
if "llm_model" not in st.session_state:
    st.session_state.llm_model = "deepseek-chat"
if "llm_base_url" not in st.session_state:
    st.session_state.llm_base_url = "https://api.deepseek.com/v1"

# 服务商选择
provider_keys = list(PROVIDER_PRESETS.keys())
provider_labels = [PROVIDER_PRESETS[k]["label"] for k in provider_keys]
current_idx = provider_keys.index(st.session_state.llm_provider) \
    if st.session_state.llm_provider in provider_keys else 0

selected_label = st.sidebar.selectbox(
    "模型服务商",
    provider_labels,
    index=current_idx,
    key="sidebar_provider",
)
selected_provider = provider_keys[provider_labels.index(selected_label)]
preset = PROVIDER_PRESETS[selected_provider]

if selected_provider != st.session_state.llm_provider:
    st.session_state.llm_provider = selected_provider
    st.session_state.llm_base_url = preset["base_url"]
    st.session_state.llm_model = preset["default_model"]
    st.rerun()

# API 密钥
is_ollama = selected_provider == "ollama"
api_key = st.sidebar.text_input(
    "API 密钥",
    type="password",
    value=st.session_state.llm_api_key,
    placeholder="sk-..." if not is_ollama else "Ollama 无需密钥",
    disabled=is_ollama,
    help="密钥仅存储在浏览器会话内存中，关闭后自动清除，永不被写入磁盘。Ollama 本地部署无需密钥。",
    key="sidebar_api_key",
)
if api_key:
    st.session_state.llm_api_key = api_key

# 安全状态提示
if st.session_state.llm_api_key or is_ollama:
    st.sidebar.caption("🔒 密钥已载入内存（不写盘）")
    if st.sidebar.button("清除密钥", key="sidebar_clear_key"):
        st.session_state.llm_api_key = ""
        st.session_state.llm_messages = []
        st.rerun()
elif not is_ollama:
    st.sidebar.caption("⚠️ 未配置密钥，助手无法使用")

# 快捷入口
st.sidebar.page_link(
    "pages/07_AI助手.py",
    label="💬 打开 AI 助手",
    help="向 AI 咨询平台使用、数据分析和模型解读",
    use_container_width=True,
)

st.sidebar.markdown("---")

# ============================================================
# 主页面
# ============================================================
st.title("🏥 北京市气候健康风险预警 — 智能体可视化平台")

st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;">
<h3 style="color: white;">🤖 全流程自动化分析智能体</h3>
<p>配置规则 → 一键启动 → 自动完成从数据采集到报告生成的全链路分析。</p>
<p>仅在数据异常、模型失效等场景触发人工复核。</p>
</div>
""", unsafe_allow_html=True)

# 流程概览
st.header("📋 分析流程")

col1, col2, col3, col4, col5, col6 = st.columns(6)

steps = [
    ("📥", "数据采集", "多源爬虫调度"),
    ("🔧", "数据清洗", "自适应质控"),
    ("📊", "数据可视化", "多维图表"),
    ("🤖", "建模训练", "AutoML自适应"),
    ("📈", "模型评测", "全维度诊断"),
    ("📄", "报告生成", "一键导出"),
]

for col, (icon, title, desc) in zip([col1, col2, col3, col4, col5, col6], steps):
    with col:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 8px;">
            <div style="font-size: 2em;">{icon}</div>
            <div style="font-weight: bold;">{title}</div>
            <div style="font-size: 0.8em; color: #666;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# 数据概览
st.header("📊 当前数据概览")

if os.path.exists(weather_path):
    try:
        weather_df = pd.read_csv(weather_path, encoding="utf-8-sig")
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("气象记录数", f"{len(weather_df):,}")
        with col_b:
            st.metric("覆盖行政区", str(weather_df["district"].nunique() if "district" in weather_df.columns else "N/A"))
        with col_c:
            date_range = f"{weather_df['date'].min()} ~ {weather_df['date'].max()}" if "date" in weather_df.columns else "N/A"
            st.metric("时间范围", date_range)
        with col_d:
            sources = weather_df["source"].nunique() if "source" in weather_df.columns else 0
            st.metric("数据源数", sources)

        # 数据预览
        with st.expander("🔍 气象数据预览"):
            st.dataframe(weather_df.head(20), use_container_width=True)
    except Exception as e:
        st.warning(f"气象数据加载异常: {e}")
else:
    st.info("📌 气象标准数据尚未生成。请先在「数据采集」页面运行爬虫调度。")

st.markdown("---")

# 快速导航
st.header("🧭 快速导航")
nav_cols = st.columns(3)
nav_items = [
    ("📥 数据采集", "pages/01_数据采集.py", "配置并运行多源数据爬虫"),
    ("🔧 数据管理", "pages/02_数据管理.py", "上传数据、清洗配置、质控预览"),
    ("📊 数据可视化", "pages/03_数据可视化.py", "气象分布、疾病趋势、关联分析"),
    ("🤖 建模训练", "pages/04_建模训练.py", "特征选择、AutoML、模型对比"),
    ("📈 模型评测", "pages/05_模型评测.py", "全指标诊断、SHAP可解释性"),
    ("📄 报告生成", "pages/06_报告生成.py", "一键出报告、批量下载"),
]

for i, (title, page, desc) in enumerate(nav_items):
    with nav_cols[i % 3]:
        with st.container(border=True):
            st.page_link(page, label=title, help=desc, use_container_width=True)
            st.caption(desc)

st.markdown("---")
st.caption(f"© 2026 北京市气候健康风险预警平台 | 数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
