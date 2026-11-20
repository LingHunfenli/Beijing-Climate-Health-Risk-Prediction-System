"""重新生成图3-1：全中文架构图，解决乱码"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

# 显式加载 SimHei 字体
font_path = None
for f in fm.fontManager.ttflist:
    if f.name == 'SimHei':
        font_path = f.fname
        break

if font_path:
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    font_name = prop.get_name()
else:
    font_name = 'SimHei'

plt.rcParams['font.sans-serif'] = [font_name, 'Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# Also register the font explicitly
from matplotlib import font_manager
font_manager.fontManager.addfont(font_path) if font_path else None

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis('off')

colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']
layer_names = ['展现层', '业务层', '计算层', '数据层']
layer_descs = [
    'Streamlit Web 交互界面\n├ 首页仪表板         ├ 数据采集页面\n├ 数据管理页面       ├ 数据可视化页面\n├ 建模训练页面       ├ 模型评测页面\n├ 报告生成页面       └ AI 助手页面',
    'AgentPipeline 配置驱动调度引擎\n├ CrawlAgent 数据采集智能体\n├ CleanAgent 数据清洗智能体\n├ FeatureEngineer 特征工程\n├ ModelAgent 自适应建模智能体\n├ EvalAgent 模型评测智能体\n├ ReportAgent 报告生成智能体\n└ ProvenanceTracker 溯源追踪',
    '核心算法计算层\n├ 特征工程流水线（聚合 / 滞后 / 滑动窗 / 哑变量）\n├ 十模型池（LightGBM / XGBoost / 随机森林 / SVR 等）\n├ 七项指标评测 + 过拟合 / 欠拟合检测\n├ SHAP 可解释性分析 + 残差诊断\n└ Jinja2 模板引擎自动报告渲染',
    '多源异构数据接入层\n├ 国家气象信息中心 ─ 地面气象观测 + 高空探空观测\n├ 中国天气网 ─ 历史均值 / 实况 / 天气预报\n├ 天气后报网 ─ 历史气象实况数据\n├ 北京市卫健委 ─ 法定传染病疫情月报\n├ 中国疾控中心 ─ 全国传染病监测数据\n└ 文献数据 ─ PDF / Excel 格式化提取',
]

y_positions = [5.5, 3.5, 1.5, -0.5]

for i in range(4):
    y = y_positions[i]
    # 层背景
    rect = plt.Rectangle((0, y), 12, 1.8, facecolor=colors[i], alpha=0.12,
                          edgecolor=colors[i], linewidth=2, linestyle='-',
                          joinstyle='round')
    ax.add_patch(rect)

    # 层标签
    ax.text(0.3, y + 1.55, layer_names[i], fontsize=14, fontweight='bold',
            color=colors[i], va='top')

    # 层内容
    ax.text(6, y + 0.9, layer_descs[i], fontsize=8.5, ha='center', va='center',
            fontfamily=font_name,
            bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                       edgecolor=colors[i], alpha=0.9))

# 层间箭头
for i in range(3):
    y_from = y_positions[i]
    y_to = y_positions[i + 1]
    ax.annotate('', xy=(6, y_to + 1.8), xytext=(6, y_from),
                arrowprops=dict(arrowstyle='->', color='#333333',
                                lw=2.5, connectionstyle='arc3,rad=0'))

# 标题
ax.set_title('图3-1  系统四层总体架构示意图', fontsize=16, fontweight='bold', pad=15)

plt.tight_layout()
output_path = 'output/charts/c3.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

print(f"架构图已重新生成: {output_path}")
print(f"使用字体: {font_name}")
print(f"字体路径: {font_path}")
