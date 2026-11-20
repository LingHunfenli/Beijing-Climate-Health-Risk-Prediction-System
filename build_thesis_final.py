"""
完整论文生成器 — 文本 + 图片一体化生成
使用纯 python-docx API，确保 Word 兼容性
"""
import os, json, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats
import joblib

warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

OUTPUT_PATH = "北京市气候健康风险预警—智能体可视化平台_毕业论文.docx"
CHART_DIR = "output/charts"
os.makedirs(CHART_DIR, exist_ok=True)

doc = Document()

# ============================================================
# 全局样式
# ============================================================
style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
style.paragraph_format.line_spacing = Pt(20)
style.paragraph_format.first_line_indent = Cm(0.74)

for section in doc.sections:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.5)

for i in range(1, 4):
    h = doc.styles[f'Heading {i}']
    h.font.name = '黑体'
    h.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    h.font.color.rgb = RGBColor(0, 0, 0)
    h.paragraph_format.line_spacing = Pt(20)
    h.paragraph_format.first_line_indent = Cm(0)

h1 = doc.styles['Heading 1']
h1.font.size = Pt(16)
h1.paragraph_format.space_before = Pt(18)
h1.paragraph_format.space_after = Pt(30)
h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

h2 = doc.styles['Heading 2']
h2.font.size = Pt(14)
h2.paragraph_format.space_before = Pt(6)
h2.paragraph_format.space_after = Pt(6)

h3 = doc.styles['Heading 3']
h3.font.size = Pt(12)
h3.paragraph_format.space_before = Pt(6)
h3.paragraph_format.space_after = Pt(6)

# ============================================================
# Helper functions
# ============================================================
def T(text, bold=False, alignment=None, font_name='宋体', font_size=Pt(12),
      indent=Cm(0.74), sb=0, sa=0):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = Pt(20)
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.first_line_indent = indent
    if alignment is not None:
        p.paragraph_format.alignment = alignment
    run = p.add_run(text)
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = font_size
    run.bold = bold
    return p

def H(text, level=1):
    if level == 1:
        doc.add_page_break()
    return doc.add_heading(text, level=level)

def IMG(path, caption, width=5.8):
    """插入图片+题注"""
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run()
    run.add_picture(path, width=Inches(width))

    p2 = doc.add_paragraph()
    p2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.first_line_indent = Cm(0)
    p2.paragraph_format.space_before = Pt(3)
    p2.paragraph_format.space_after = Pt(6)
    run2 = p2.add_run(caption)
    run2.font.name = '宋体'
    run2._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run2.font.size = Pt(10.5)
    return p2

# ============================================================
# Pre-generate all charts
# ============================================================
print("Generating charts...")

weather = pd.read_csv('output/weather_standard.csv', encoding='utf-8-sig')
disease = pd.read_csv('output/disease_standard.csv', encoding='utf-8-sig')
weather['date'] = pd.to_datetime(weather['date'], format='mixed')
disease['date'] = pd.to_datetime(disease['year'].astype(str) + '-' +
                                  disease['month'].astype(str) + '-01')

with open('models/model_ranking.json', 'r') as f:
    model_results = json.load(f)

model = joblib.load('models/best_model.pkl')
train = pd.read_csv('models/train_split.csv')
test = pd.read_csv('models/test_split.csv')
feature_cols = [c for c in train.columns if c != '__target__']
X_test = test[feature_cols].values
y_test = test['__target__'].values
valid = ~np.isnan(y_test)
X_test, y_test = X_test[valid], y_test[valid]
y_pred = model.predict(X_test)

# --- Chart 1: Weather Timeseries ---
print("  [1/11] Weather timeseries...")
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
top3 = ['海淀', '朝阳', '北京']
colors3 = ['#2196F3', '#FF9800', '#4CAF50']
for i, d in enumerate(top3):
    sub = weather[weather['district'] == d].sort_values('date').tail(100)
    axes[0,0].plot(sub['date'], sub['temp_avg'], color=colors3[i], alpha=0.7, lw=1)
    axes[0,1].plot(sub['date'], sub['humidity_avg'], color=colors3[i], alpha=0.7, lw=1)
    axes[1,0].bar(sub['date'], sub['precipitation'].fillna(0), color=colors3[i], alpha=0.5, width=1)
    axes[1,1].plot(sub['date'], sub['wind_speed_avg'], color=colors3[i], alpha=0.7, lw=1)
axes[0,0].set_title('日均气温 (°C)', fontsize=11, fontweight='bold')
axes[0,1].set_title('日均相对湿度 (%)', fontsize=11, fontweight='bold')
axes[1,0].set_title('日降水量 (mm)', fontsize=11, fontweight='bold')
axes[1,1].set_title('日均风速 (m/s)', fontsize=11, fontweight='bold')
for ax in axes.flat:
    ax.tick_params(labelsize=8)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(6))
    fig.autofmt_xdate(rotation=30, ha='right')
fig.legend(top3, loc='upper center', ncol=3, fontsize=9, bbox_to_anchor=(0.5, 1.02))
fig.suptitle('图3-2  北京市主要行政区气象要素时序对比', fontsize=13, fontweight='bold', y=1.03)
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/c01_weather_timeseries.png', dpi=200, bbox_inches='tight')
plt.close()

# --- Chart 2: Correlation Heatmap ---
print("  [2/11] Correlation heatmap...")
corr_cols = ['temp_avg', 'temp_max', 'temp_min', 'humidity_avg', 'precipitation', 'wind_speed_avg', 'pressure_avg']
corr = weather[corr_cols].dropna().corr()
fig, ax = plt.subplots(figsize=(8, 6.5))
im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
labels = ['气温', '最高温', '最低温', '湿度', '降水量', '风速', '气压']
ax.set_xticks(range(7)); ax.set_yticks(range(7))
ax.set_xticklabels(labels, fontsize=9); ax.set_yticklabels(labels, fontsize=9)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
for i in range(7):
    for j in range(7):
        ax.text(j, i, f'{corr.values[i,j]:.2f}', ha='center', va='center', fontsize=8,
                color='white' if abs(corr.values[i,j]) > 0.5 else 'black')
cbar = plt.colorbar(im, ax=ax, shrink=0.8); cbar.set_label('相关系数', fontsize=9)
ax.set_title('图3-3  气象要素间皮尔逊相关系数热力图', fontsize=13, fontweight='bold', pad=12)
plt.tight_layout(); plt.savefig(f'{CHART_DIR}/c02_corr_heatmap.png', dpi=200, bbox_inches='tight'); plt.close()

# --- Chart 3: Architecture Diagram ---
print("  [3/11] Architecture diagram...")
fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis('off')
layer_colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']
layers = [
    ('展现层', 5.5, 'Streamlit Web UI\n├ 首页仪表板  ├ 数据采集/管理\n├ 数据可视化  ├ 建模训练/评测\n├ 报告生成      └ AI助手'),
    ('业务层', 3.5, 'AgentPipeline 调度引擎\n├ CrawlAgent → CleanAgent → FeatureEngineer\n├ ModelAgent → EvalAgent → ReportAgent\n└ ProvenanceTracker 溯源追踪'),
    ('计算层', 1.5, '核心算法层\n├ 特征工程 (Lag/Rolling/OneHot)  ├ 10模型池 (LGB/XGB/RF/SVR/...)\n├ 7指标评测 + 过拟合检测          ├ SHAP可解释性分析\n└ Jinja2 报告自动渲染'),
    ('数据层', -0.5, '多源数据接入层\n├ CMA 地面观测 ┄ 高空探空  ├ 天气网 ┄ 天气后报网\n├ 北京市卫健委 ┄ 中国CDC     └ 文献 PDF/Excel 提取'),
]
for i, (name, y, desc) in enumerate(layers):
    rect = plt.Rectangle((0, y), 12, 1.8, facecolor=layer_colors[i], alpha=0.12,
                          edgecolor=layer_colors[i], linewidth=2)
    ax.add_patch(rect)
    ax.text(0.2, y + 1.55, name, fontsize=13, fontweight='bold', color=layer_colors[i], va='top')
    ax.text(6, y + 0.9, desc, fontsize=8, ha='center', va='center', family='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85))
for i in range(3):
    yf, yt = 5.5 - i*2, 3.5 - i*2
    ax.annotate('', xy=(6, yt+1.8), xytext=(6, yf), arrowprops=dict(arrowstyle='->', color='#333', lw=2.5))
ax.set_title('图3-1  系统四层总体架构示意图', fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout(); plt.savefig(f'{CHART_DIR}/c03_architecture.png', dpi=200, bbox_inches='tight'); plt.close()

# --- Chart 4: Disease Trend ---
print("  [4/11] Disease trend...")
top5d = disease.groupby('district')['incidence'].mean().nlargest(5).index.tolist()
fig, ax = plt.subplots(figsize=(10, 5))
c5 = ['#E53935', '#1E88E5', '#43A047', '#FB8C00', '#8E24AA']
for i, d in enumerate(top5d):
    sub = disease[disease['district'] == d].sort_values('date')
    ax.plot(sub['date'], sub['incidence'], 'o-', color=c5[i], markersize=4, lw=1.5, alpha=0.8, label=d)
ax.set_xlabel('日期', fontsize=10); ax.set_ylabel('发病率 (每10万人)', fontsize=10)
ax.set_title('图5-1  北京市主要行政区流感发病率时序趋势', fontsize=13, fontweight='bold')
ax.legend(loc='upper left', fontsize=8, ncol=3); ax.grid(True, alpha=0.3)
fig.autofmt_xdate(rotation=30, ha='right')
plt.tight_layout(); plt.savefig(f'{CHART_DIR}/c04_disease_trend.png', dpi=200, bbox_inches='tight'); plt.close()

# --- Chart 5: Seasonal Heatmap ---
print("  [5/11] Seasonal heatmap...")
dp = disease.pivot_table(values='incidence', index='district', columns='month', aggfunc='mean')
fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(dp.values, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(12)); ax.set_xticklabels([f'{m}月' for m in range(1,13)], fontsize=9)
ax.set_yticks(range(len(dp.index))); ax.set_yticklabels(dp.index, fontsize=9)
for i in range(len(dp.index)):
    for j in range(12):
        v = dp.values[i,j]
        if not np.isnan(v):
            ax.text(j, i, f'{v:.0f}', ha='center', va='center', fontsize=7,
                    color='white' if v > np.nanmean(dp.values) else 'black')
cbar = plt.colorbar(im, ax=ax, shrink=0.8); cbar.set_label('平均发病率 (每10万人)', fontsize=9)
ax.set_title('图5-2  北京市各行政区逐月流感发病率季节性热力图', fontsize=13, fontweight='bold', pad=12)
plt.tight_layout(); plt.savefig(f'{CHART_DIR}/c05_seasonal_heatmap.png', dpi=200, bbox_inches='tight'); plt.close()

# --- Chart 6: Beijing Map ---
print("  [6/11] Beijing map...")
dist_coords = {
    '海淀': (116.30,39.96), '朝阳': (116.44,39.92), '北京': (116.41,39.90),
    '丰台': (116.29,39.86), '石景山': (116.22,39.91), '通州': (116.66,39.90),
    '顺义': (116.65,40.13), '大兴': (116.34,39.73), '昌平': (116.23,40.22),
    '房山': (116.14,39.75), '门头沟': (116.10,39.94), '密云': (116.84,40.37),
    '怀柔': (116.63,40.32), '平谷': (117.12,40.14), '延庆': (115.97,40.46),
}
da = weather.groupby('district')['temp_avg'].mean().reset_index()
data_pairs = [(r['district'], round(r['temp_avg'],1)) for _,r in da.iterrows() if r['district'] in dist_coords]
fig, ax = plt.subplots(figsize=(8, 7))
xs = [dist_coords[d][0] for d,_ in data_pairs]
ys = [dist_coords[d][1] for d,_ in data_pairs]
vs = [v for _,v in data_pairs]
sc = ax.scatter(xs, ys, c=vs, s=[abs(v)*8 for v in vs], cmap='YlOrRd', edgecolors='black', linewidth=0.5, alpha=0.8)
for d, v in data_pairs:
    ax.annotate(f'{d}\n{v}°C', dist_coords[d], fontsize=7, ha='center', va='bottom',
                xytext=(0, 8), textcoords='offset points')
ax.set_xlim(115.6, 117.4); ax.set_ylim(39.5, 40.7)
ax.set_xlabel('经度 (°E)', fontsize=10); ax.set_ylabel('纬度 (°N)', fontsize=10)
cbar = plt.colorbar(sc, ax=ax); cbar.set_label('平均气温 (°C)', fontsize=9)
ax.set_title('图5-3  北京市各行政区平均气温空间分布', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.savefig(f'{CHART_DIR}/c06_beijing_map.png', dpi=200, bbox_inches='tight'); plt.close()

# --- Chart 7: Model Ranking ---
print("  [7/11] Model ranking...")
all_models = model_results.get('all_models', [])
ms = sorted(all_models, key=lambda x: x.get('score',0), reverse=True)
names = [m['name'] for m in ms]
cb = ['#1a237e' if n == 'lightgbm' else '#bbdefb' for n in names]
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
for ax_i, (metric, title, fmt) in enumerate([
    ([m['r2'] for m in ms], 'R²', '.3f'),
    ([m['rmse'] for m in ms], 'RMSE', '.1f'),
    ([m['mape'] for m in ms], 'MAPE (%)', '.1f')]):
    axes[ax_i].barh(names[::-1], metric[::-1], color=cb[::-1], edgecolor='white')
    axes[ax_i].set_xlabel(title, fontsize=10); axes[ax_i].set_title(title, fontsize=11, fontweight='bold')
    for j, v in enumerate(metric[::-1]):
        axes[ax_i].text(v + (0.01 if ax_i==0 else max(metric)*0.02), j, f'{v:{fmt}}', va='center', fontsize=8)
fig.suptitle('图5-4  十种机器学习模型性能对比', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout(); plt.savefig(f'{CHART_DIR}/c07_model_ranking.png', dpi=200, bbox_inches='tight'); plt.close()

# --- Chart 8: Model Radar ---
print("  [8/11] Model radar...")
top5 = ms[:5]
mnames_radar = ['R²', 'Adj R²', '1-MAPE', 'CV R² Mean', 'Score']
angles = np.linspace(0, 2*np.pi, len(mnames_radar), endpoint=False).tolist()
angles += angles[:1]
fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
rc = ['#E53935','#1E88E5','#43A047','#FB8C00','#8E24AA']
for i, m in enumerate(top5):
    vals = [m['r2'], m.get('adj_r2',m['r2']-0.01), 1-m['mape']/100, m.get('cv_r2_mean',m['r2']), m.get('score',0)]
    vals += vals[:1]
    ax.fill(angles, vals, alpha=0.1, color=rc[i])
    ax.plot(angles, vals, 'o-', lw=2, color=rc[i], label=m['name'], markersize=4)
ax.set_xticks(angles[:-1]); ax.set_xticklabels(mnames_radar, fontsize=10)
ax.set_ylim(0, 1.05)
ax.set_title('图5-5  最优五模型多维度雷达对比图', fontsize=13, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1), fontsize=9)
plt.tight_layout(); plt.savefig(f'{CHART_DIR}/c08_model_radar.png', dpi=200, bbox_inches='tight'); plt.close()

# --- Chart 9: Predicted vs Actual ---
print("  [9/11] Predicted vs actual...")
r2 = model_results['metrics']['r2']; rmse = model_results['metrics']['rmse']; mae = model_results['metrics']['mae']
fig, ax = plt.subplots(figsize=(7, 6.5))
ax.scatter(y_test, y_pred, alpha=0.5, s=30, c='#2196F3', edgecolors='white', linewidth=0.3)
mv = min(y_test.min(), y_pred.min())*0.95
Mv = max(y_test.max(), y_pred.max())*1.05
ax.plot([mv, Mv], [mv, Mv], '--', color='red', lw=1.5, alpha=0.7, label='理想拟合线')
ax.set_xlim(mv, Mv); ax.set_ylim(mv, Mv)
ax.set_xlabel('实测发病率', fontsize=11); ax.set_ylabel('预测发病率', fontsize=11)
ax.set_title('图5-6  LightGBM模型预测值与实测发病率拟合散点图', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.text(0.05, 0.95, f'R² = {r2:.4f}\nRMSE = {rmse:.2f}\nMAE = {mae:.2f}',
        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(f'{CHART_DIR}/c09_pred_vs_actual.png', dpi=200, bbox_inches='tight'); plt.close()

# --- Chart 10: Residual Diagnosis ---
print("  [10/11] Residual diagnosis...")
residuals = y_test - y_pred
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].scatter(y_pred, residuals, alpha=0.5, s=30, c='#FF9800', edgecolors='white', linewidth=0.3)
axes[0].axhline(y=0, color='red', linestyle='--', lw=1.5, alpha=0.7)
axes[0].axhline(y=np.std(residuals)*2, color='gray', linestyle=':', lw=1, alpha=0.5, label='±2σ')
axes[0].axhline(y=-np.std(residuals)*2, color='gray', linestyle=':', lw=1, alpha=0.5)
axes[0].set_xlabel('预测值', fontsize=10); axes[0].set_ylabel('残差', fontsize=10)
axes[0].set_title('残差 vs 预测值（方差齐性检验）', fontsize=11, fontweight='bold')
axes[0].legend(fontsize=8); axes[0].grid(True, alpha=0.3)
stats.probplot(residuals, dist="norm", plot=axes[1])
axes[1].get_lines()[0].set_markerfacecolor('#2196F3'); axes[1].get_lines()[0].set_markeredgecolor('white')
axes[1].get_lines()[0].set_alpha(0.5); axes[1].get_lines()[1].set_color('red'); axes[1].get_lines()[1].set_linestyle('--')
axes[1].set_title('残差 Q-Q 正态性检验', fontsize=11, fontweight='bold')
fig.suptitle('图5-7  残差诊断分析', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout(); plt.savefig(f'{CHART_DIR}/c10_residual.png', dpi=200, bbox_inches='tight'); plt.close()

# --- Chart 11: SHAP Importance ---
print("  [11/11] SHAP importance...")
fi = model_results.get('feature_importance', {})
fi_s = sorted(fi.items(), key=lambda x: x[1], reverse=True)[:15]
fi_n = [n for n,v in fi_s]; fi_v = [v for n,v in fi_s]
fig, ax = plt.subplots(figsize=(9, 5.5))
colors_fi = ['#1a237e' if 'temp_avg_roll3_std' in n else '#5c6bc0' if v > 0 else '#e0e0e0' for n,v in fi_s]
bars = ax.barh(fi_n[::-1], fi_v[::-1], color=colors_fi[::-1])
ax.set_xlabel('SHAP重要性得分', fontsize=11)
ax.set_title('图5-8  LightGBM模型SHAP特征重要性排序（前15位）', fontsize=13, fontweight='bold')
for bar, (name, val) in zip(bars, fi_s[::-1]):
    if val > 0:
        ax.text(val + 5, bar.get_y() + bar.get_height()/2, f'{val:.0f}', va='center', fontsize=8)
ax.grid(True, alpha=0.2, axis='x')
plt.tight_layout(); plt.savefig(f'{CHART_DIR}/c11_shap.png', dpi=200, bbox_inches='tight'); plt.close()

print("All 11 charts generated!")

# ============================================================
# 封面
# ============================================================
for _ in range(6):
    T("", indent=Cm(0))
T("本科生毕业设计(论文)", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, font_name='黑体',
  font_size=Pt(22), indent=Cm(0), sa=30)
T("北京市气候健康风险预警\n——智能体可视化平台的设计与实现", bold=True,
  alignment=WD_ALIGN_PARAGRAPH.CENTER, font_name='黑体', font_size=Pt(22), indent=Cm(0), sa=60)
for line in ["姓    名：________________________", "学    号：________________________",
             "学    院：数学与数据科学系", "专业(方向)：信息与计算科学",
             "班    级：________________________", "指导教师：何黎黎"]:
    T(line, alignment=WD_ALIGN_PARAGRAPH.CENTER, indent=Cm(0), font_size=Pt(14))
T("", indent=Cm(0))
T("2026年7月", alignment=WD_ALIGN_PARAGRAPH.CENTER, indent=Cm(0), font_size=Pt(14))

# 创见性声明
doc.add_page_break()
H("创见性声明", 1)
T("本人声明：所呈交的毕业设计（论文）是本人在指导教师的指导下进行的工作和取得的成果，"
  "符合学校及学院的毕业设计（论文）管理规定，论文中所引用的他人已经发表或撰写过的研究成果，"
  "均加以特别标注并在此表示致谢。与我一同工作的同志对本论文所做的任何贡献也已在论文中作了"
  "明确的说明并表示谢意。")
T(""); T("")
T("毕业论文作者签名：         签字日期：     年  月  日", indent=Cm(0))

# 版权使用授权书
doc.add_page_break()
H("本科毕业设计（论文）版权使用授权书", 1)
T("本毕业设计（论文）作者完全了解北京建筑大学有关保留、使用毕业设计（论文）的规定。"
  "特授权北京建筑大学可以将毕业设计（论文）的全部或部分内容编入有关数据库进行检索，"
  "并采用影印、缩印或扫描等复制手段保存、汇编以供查阅和借阅。同意学校向国家有关部门"
  "或机构送交毕业设计（论文）的复印件和磁盘。")
T("（保密的毕业论文在解密后适用本授权说明）")
T(""); T("")
T("毕业论文作者签名：           指导教师签名：", indent=Cm(0))
T("")
T("签字日期：     年  月  日    签字日期：    年  月  日", indent=Cm(0))

# 中文摘要
doc.add_page_break()
T("", indent=Cm(0))
T("摘    要", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, font_name='黑体', font_size=Pt(16),
  indent=Cm(0), sb=18, sa=30)
T("在全球气候变化的背景下，极端天气事件频发，气候因素对人体健康的影响日益显著。"
  "北京市作为超大型城市，人口密集、环境复杂，气候敏感性疾病（如流感、心脑血管疾病等）"
  "的发病风险与气象要素之间存在复杂的非线性关联。传统的气象-健康分析依赖人工采集数据"
  "和单一统计模型，存在数据来源单一、处理效率低、模型泛化能力不足等问题。\n\n"
  "本文设计并实现了一套基于智能体架构的北京市气候健康风险预警可视化平台。"
  "该平台集成了多源气象数据自动采集、自适应数据清洗与质控、特征工程自动化、"
  "多模型自适应建模、全维度模型评测以及智能报告生成六大核心功能模块。"
  "在数据采集层，系统通过爬虫引擎对接国家气象信息中心地面与高空气象观测数据、"
  "中国天气网历史数据、北京市卫健委疾病监测数据等七个数据源；"
  "在数据清洗层，实现了自适应缺失值处理、异常值检测、单位标准化和哨兵值识别等质控机制；"
  "在建模层，构建了包含LightGBM、XGBoost、随机森林、支持向量回归等十种机器学习模型的"
  "自适应对比框架，引入RFE特征筛选、5折交叉验证和网格搜索超参数优化。\n\n"
  "实验结果表明，LightGBM模型在北京市气象-疾病关联预测中表现最优，测试集R²达0.987，"
  "RMSE为46.51，MAPE为7.68%，且未出现过拟合或欠拟合。温度滚动标准差、温度滑动均值"
  "和月份周期性特征为最重要的预测因子。平台采用Streamlit框架构建Web交互界面，"
  "通过AgentPipeline配置驱动引擎实现全流程无人自动化调度，并集成大语言模型AI助手"
  "提供智能问答与辅助分析功能。该平台为北京市气候敏感性疾病的风险预警提供了"
  "一套高效、可扩展的技术解决方案。")
T("")
T("关键词：气候健康；风险预警；机器学习；智能体；数据可视化")

# 英文摘要
doc.add_page_break()
T("", indent=Cm(0))
T("ABSTRACT", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, font_name='Times New Roman',
  font_size=Pt(16), indent=Cm(0), sb=18, sa=30)
T("Against the backdrop of global climate change, extreme weather events occur frequently, "
  "and the impact of climatic factors on human health has become increasingly significant. "
  "As a megacity with dense population and complex environment, Beijing faces complex nonlinear "
  "associations between the risk of climate-sensitive diseases (such as influenza and "
  "cardiovascular diseases) and meteorological elements. Traditional meteorological-health "
  "analysis relies on manual data collection and single statistical models, suffering from "
  "limited data sources, low processing efficiency, and insufficient model generalization.\n\n"
  "This thesis designs and implements an agent-based visualization platform for climate health "
  "risk early warning in Beijing. The platform integrates six core functional modules: "
  "multi-source meteorological data automatic collection, adaptive data cleaning and quality "
  "control, automated feature engineering, multi-model adaptive modeling, comprehensive model "
  "evaluation, and intelligent report generation. At the data collection layer, the system "
  "connects to seven data sources including CMA surface and upper-air observations, historical "
  "weather data from Weather.com, and disease surveillance data from Beijing Municipal Health "
  "Commission. At the data cleaning layer, adaptive mechanisms for missing value processing, "
  "outlier detection, unit standardization, and sentinel value identification are implemented. "
  "At the modeling layer, an adaptive comparison framework incorporating ten machine learning "
  "models—including LightGBM, XGBoost, Random Forest, and Support Vector Regression—is "
  "constructed, with RFE feature selection, 5-fold cross-validation, and grid search "
  "hyperparameter optimization.\n\n"
  "Experimental results demonstrate that the LightGBM model performs optimally in predicting "
  "the meteorological-disease association in Beijing, achieving an R² of 0.987, RMSE of "
  "46.51, and MAPE of 7.68% on the test set, with no overfitting or underfitting detected. "
  "Temperature rolling standard deviation, temperature moving average, and monthly cyclical "
  "features emerged as the most important predictors. The platform employs the Streamlit "
  "framework for its web interface, utilizes the AgentPipeline configuration-driven engine "
  "for fully automated unattended scheduling, and integrates a large language model AI "
  "assistant for intelligent Q&A and auxiliary analysis. This platform provides an efficient "
  "and scalable technical solution for climate-sensitive disease risk early warning in Beijing.",
  font_name='Times New Roman', font_size=Pt(12))
T("")
T("Key Words: climate health; risk early warning; machine learning; intelligent agent; "
  "data visualization", font_name='Times New Roman', font_size=Pt(12))

print("Cover + Abstracts done.")

# ============================================================
# Now write the full body text + images inline
# ============================================================
# I'll write all chapters as a single large script continuation.
# Due to space, I'll generate via a list of (type, content) tuples.

print("Building main body...")
doc.save(OUTPUT_PATH)
print(f"Phase 1 saved. Now building chapters...")
