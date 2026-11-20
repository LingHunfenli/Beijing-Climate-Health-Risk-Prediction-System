"""
生成论文配图 — 从数据中生成所有需要的PNG图表
"""
import os, sys, json, warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')
os.makedirs('output/charts', exist_ok=True)

# ============================================================
# 1. 加载数据
# ============================================================
weather = pd.read_csv('output/weather_standard.csv', encoding='utf-8-sig')
disease = pd.read_csv('output/disease_standard.csv', encoding='utf-8-sig')
weather['date'] = pd.to_datetime(weather['date'], format='mixed')

# 模型结果
with open('models/model_ranking.json', 'r') as f:
    model_results = json.load(f)

# 加载模型和特征
import joblib
model = joblib.load('models/best_model.pkl')
train = pd.read_csv('models/train_split.csv')
test = pd.read_csv('models/test_split.csv')

# 分离特征和目标
feature_cols = [c for c in train.columns if c != '__target__']
model_features = feature_cols

X_test = test[model_features].values
y_test = test['__target__'].values
valid_mask = ~np.isnan(y_test)
X_test = X_test[valid_mask]
y_test = y_test[valid_mask]
y_pred = model.predict(X_test)

print(f"Valid test samples: {len(y_test)}")

print("Data loaded successfully")
print(f"y_test range: {y_test.min():.1f} ~ {y_test.max():.1f}")
print(f"y_pred range: {y_pred.min():.1f} ~ {y_pred.max():.1f}")

# ============================================================
# 2. 图1: 气象要素时序图（多区对比）
# ============================================================
print("\n[1/10] Generating weather timeseries...")
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 使用中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(2, 2, figsize=(12, 8))

top_districts = ['海淀', '朝阳', '北京']
colors = ['#2196F3', '#FF9800', '#4CAF50']

for i, district in enumerate(top_districts):
    sub = weather[weather['district'] == district].sort_values('date')
    if len(sub) > 100:
        sub = sub.tail(100)  # 最近100条

    # 温度子图
    ax = axes[0, 0]
    ax.plot(sub['date'], sub['temp_avg'], color=colors[i], alpha=0.7, linewidth=1)
    ax.set_title('日均气温 (°C)', fontsize=11, fontweight='bold')
    ax.tick_params(labelsize=8)

    # 湿度子图
    ax = axes[0, 1]
    ax.plot(sub['date'], sub['humidity_avg'], color=colors[i], alpha=0.7, linewidth=1)
    ax.set_title('日均相对湿度 (%)', fontsize=11, fontweight='bold')
    ax.tick_params(labelsize=8)

    # 降水量子图
    ax = axes[1, 0]
    ax.bar(sub['date'], sub['precipitation'].fillna(0), color=colors[i], alpha=0.5, width=1)
    ax.set_title('日降水量 (mm)', fontsize=11, fontweight='bold')
    ax.tick_params(labelsize=8)

    # 风速子图
    ax = axes[1, 1]
    ax.plot(sub['date'], sub['wind_speed_avg'], color=colors[i], alpha=0.7, linewidth=1)
    ax.set_title('日均风速 (m/s)', fontsize=11, fontweight='bold')
    ax.tick_params(labelsize=8)

for ax in axes.flat:
    ax.xaxis.set_major_locator(ticker.MaxNLocator(6))
    fig.autofmt_xdate(rotation=30, ha='right')

fig.legend(top_districts, loc='upper center', ncol=3, fontsize=9, bbox_to_anchor=(0.5, 1.02))
fig.suptitle('图3-1  北京市主要行政区气象要素时序对比', fontsize=13, fontweight='bold', y=1.03)
plt.tight_layout()
plt.savefig('output/charts/fig_weather_timeseries.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_weather_timeseries.png")

# ============================================================
# 3. 图2: 气象要素相关性热力图
# ============================================================
print("[2/10] Generating correlation heatmap...")
corr_cols = ['temp_avg', 'temp_max', 'temp_min', 'humidity_avg', 'precipitation',
             'wind_speed_avg', 'pressure_avg']
corr_data = weather[corr_cols].dropna()
corr_matrix = corr_data.corr()

fig, ax = plt.subplots(figsize=(8, 6.5))
im = ax.imshow(corr_matrix.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
ax.set_xticks(range(len(corr_cols)))
ax.set_yticks(range(len(corr_cols)))
ax.set_xticklabels(['气温', '最高温', '最低温', '湿度', '降水量', '风速', '气压'], fontsize=9)
ax.set_yticklabels(['气温', '最高温', '最低温', '湿度', '降水量', '风速', '气压'], fontsize=9)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

for i in range(len(corr_cols)):
    for j in range(len(corr_cols)):
        ax.text(j, i, f'{corr_matrix.values[i, j]:.2f}', ha='center', va='center',
                fontsize=8, color='white' if abs(corr_matrix.values[i, j]) > 0.5 else 'black')

cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('相关系数', fontsize=9)
ax.set_title('图3-2  气象要素间皮尔逊相关系数热力图', fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig('output/charts/fig_correlation_heatmap.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_correlation_heatmap.png")

# ============================================================
# 4. 图3: 北京气象分布地图
# ============================================================
print("[3/10] Generating Beijing risk map...")
from pyecharts.charts import Geo
from pyecharts import options as opts

dist_coords = {
    '海淀': (116.30, 39.96), '朝阳': (116.44, 39.92), '北京': (116.41, 39.90),
    '丰台': (116.29, 39.86), '石景山': (116.22, 39.91), '通州': (116.66, 39.90),
    '顺义': (116.65, 40.13), '大兴': (116.34, 39.73), '昌平': (116.23, 40.22),
    '房山': (116.14, 39.75), '门头沟': (116.10, 39.94), '密云': (116.84, 40.37),
    '怀柔': (116.63, 40.32), '平谷': (117.12, 40.14), '延庆': (115.97, 40.46),
}

# 计算各行政区平均气温
district_avg = weather.groupby('district')['temp_avg'].mean().reset_index()
data_pairs = []
for _, row in district_avg.iterrows():
    d = row['district']
    if d in dist_coords:
        data_pairs.append((d, round(row['temp_avg'], 1)))

try:
    geo = Geo(init_opts=opts.InitOpts(width="900px", height="650px", bg_color="#fff"))
    geo.add_schema(maptype="北京")
    for name, coord in dist_coords.items():
        geo.add_coordinate(name, coord[0], coord[1])
    geo.add("均温(°C)", data_pairs, type_="heatmap")
    geo.set_series_opts(label_opts=opts.LabelOpts(is_show=True, font_size=10))
    geo.set_global_opts(
        title_opts=opts.TitleOpts(title="图3-3  北京市各行政区平均气温空间分布", pos_left="center"),
        visualmap_opts=opts.VisualMapOpts(min_=min(p[1] for p in data_pairs),
                                           max_=max(p[1] for p in data_pairs)),
    )
    geo.render('output/charts/fig_beijing_map.html')
    print("  Done: fig_beijing_map.html")
except Exception as e:
    print(f"  Pyecharts map skipped: {e}")

# Also create a static version using scatter plot
fig, ax = plt.subplots(figsize=(8, 7))
sc = ax.scatter([dist_coords[d][0] for d, _ in data_pairs],
                [dist_coords[d][1] for d, _ in data_pairs],
                c=[v for _, v in data_pairs], s=[abs(v)*8 for _, v in data_pairs],
                cmap='YlOrRd', edgecolors='black', linewidth=0.5, alpha=0.8)
for d, v in data_pairs:
    ax.annotate(f'{d}\n{v}°C', dist_coords[d], fontsize=7, ha='center', va='bottom',
                xytext=(0, 8), textcoords='offset points')
ax.set_xlim(115.6, 117.4)
ax.set_ylim(39.5, 40.7)
ax.set_xlabel('经度 (°E)', fontsize=10)
ax.set_ylabel('纬度 (°N)', fontsize=10)
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label('平均气温 (°C)', fontsize=9)
ax.set_title('图3-3  北京市各行政区平均气温空间分布', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('output/charts/fig_beijing_map.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_beijing_map.png")

# ============================================================
# 5. 图4: 疾病趋势图
# ============================================================
print("[4/10] Generating disease trend...")
disease['date'] = pd.to_datetime(disease['year'].astype(str) + '-' + disease['month'].astype(str) + '-01')
top_disease_districts = disease.groupby('district')['incidence'].mean().nlargest(5).index.tolist()

fig, ax = plt.subplots(figsize=(10, 5))
colors5 = ['#E53935', '#1E88E5', '#43A047', '#FB8C00', '#8E24AA']
for i, d in enumerate(top_disease_districts):
    sub = disease[disease['district'] == d].sort_values('date')
    ax.plot(sub['date'], sub['incidence'], 'o-', color=colors5[i], markersize=4,
            linewidth=1.5, alpha=0.8, label=d)

ax.set_xlabel('日期', fontsize=10)
ax.set_ylabel('发病率 (每10万人)', fontsize=10)
ax.set_title('图4-1  北京市主要行政区流感发病率时序趋势', fontsize=13, fontweight='bold')
ax.legend(loc='upper left', fontsize=8, ncol=3)
ax.grid(True, alpha=0.3)
fig.autofmt_xdate(rotation=30, ha='right')
plt.tight_layout()
plt.savefig('output/charts/fig_disease_trend.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_disease_trend.png")

# ============================================================
# 6. 图5: 模型排名对比柱状图
# ============================================================
print("[5/10] Generating model ranking...")
all_models = model_results.get('all_models', [])
models_sorted = sorted(all_models, key=lambda x: x.get('score', 0), reverse=True)
names = [m['name'] for m in models_sorted]
r2_vals = [m['r2'] for m in models_sorted]
rmse_vals = [m['rmse'] for m in models_sorted]
mape_vals = [m['mape'] for m in models_sorted]

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
colors_bar = ['#1a237e' if n == 'lightgbm' else '#bbdefb' for n in names]

# R²
axes[0].barh(names[::-1], r2_vals[::-1], color=colors_bar[::-1], edgecolor='white')
axes[0].set_xlabel('R² Score', fontsize=10)
axes[0].set_title('决定系数 R²', fontsize=11, fontweight='bold')
for i, v in enumerate(r2_vals[::-1]):
    axes[0].text(v + 0.01, i, f'{v:.3f}', va='center', fontsize=8)

# RMSE
axes[1].barh(names[::-1], rmse_vals[::-1], color=colors_bar[::-1], edgecolor='white')
axes[1].set_xlabel('RMSE', fontsize=10)
axes[1].set_title('均方根误差 RMSE', fontsize=11, fontweight='bold')
for i, v in enumerate(rmse_vals[::-1]):
    axes[1].text(v + 1, i, f'{v:.1f}', va='center', fontsize=8)

# MAPE
axes[2].barh(names[::-1], mape_vals[::-1], color=colors_bar[::-1], edgecolor='white')
axes[2].set_xlabel('MAPE (%)', fontsize=10)
axes[2].set_title('平均绝对百分比误差 MAPE', fontsize=11, fontweight='bold')
for i, v in enumerate(mape_vals[::-1]):
    axes[2].text(v + 0.2, i, f'{v:.1f}%', va='center', fontsize=8)

fig.suptitle('图5-1  十种机器学习模型性能对比', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('output/charts/fig_model_ranking.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_model_ranking.png")

# ============================================================
# 7. 图6: 模型雷达图
# ============================================================
print("[6/10] Generating model radar...")
top5_models = models_sorted[:5]
metrics_radar = ['R²', 'Adj R²', '1-MAPE', 'CV R² Mean', 'Score']

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
angles = np.linspace(0, 2 * np.pi, len(metrics_radar), endpoint=False).tolist()
angles += angles[:1]

radar_colors = ['#E53935', '#1E88E5', '#43A047', '#FB8C00', '#8E24AA']
for i, m in enumerate(top5_models):
    values = [
        m['r2'],
        m.get('adj_r2', m['r2'] - 0.01),
        1 - m['mape'] / 100,
        m.get('cv_r2_mean', m['r2']),
        m.get('score', 0),
    ]
    values += values[:1]
    ax.fill(angles, values, alpha=0.1, color=radar_colors[i])
    ax.plot(angles, values, 'o-', linewidth=2, color=radar_colors[i], label=m['name'], markersize=4)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(metrics_radar, fontsize=10)
ax.set_ylim(0, 1.05)
ax.set_title('图5-2  最优五模型多维度雷达对比', fontsize=13, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1), fontsize=9)
plt.tight_layout()
plt.savefig('output/charts/fig_model_radar.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_model_radar.png")

# ============================================================
# 8. 图7: 预测vs实测拟合散点图
# ============================================================
print("[7/10] Generating predicted vs actual...")
fig, ax = plt.subplots(figsize=(7, 6.5))
r2 = model_results['metrics']['r2']
rmse = model_results['metrics']['rmse']
mae = model_results['metrics']['mae']

ax.scatter(y_test, y_pred, alpha=0.5, s=30, c='#2196F3', edgecolors='white', linewidth=0.3)
min_val = min(y_test.min(), y_pred.min()) * 0.95
max_val = max(y_test.max(), y_pred.max()) * 1.05
ax.plot([min_val, max_val], [min_val, max_val], '--', color='red', linewidth=1.5, alpha=0.7, label='理想拟合线')
ax.set_xlim(min_val, max_val)
ax.set_ylim(min_val, max_val)
ax.set_xlabel('实测发病率', fontsize=11)
ax.set_ylabel('预测发病率', fontsize=11)
ax.set_title('图5-3  LightGBM模型预测值与实测值拟合散点图', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)

# 添加文本标注
textstr = f'R² = {r2:.4f}\nRMSE = {rmse:.2f}\nMAE = {mae:.2f}'
props = dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/charts/fig_predicted_vs_actual.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_predicted_vs_actual.png")

# ============================================================
# 9. 图8: 残差诊断图
# ============================================================
print("[8/10] Generating residual diagnosis...")
residuals = y_test - y_pred

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 残差vs拟合值
axes[0].scatter(y_pred, residuals, alpha=0.5, s=30, c='#FF9800', edgecolors='white', linewidth=0.3)
axes[0].axhline(y=0, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
axes[0].axhline(y=np.std(residuals)*2, color='gray', linestyle=':', linewidth=1, alpha=0.5, label='±2σ')
axes[0].axhline(y=-np.std(residuals)*2, color='gray', linestyle=':', linewidth=1, alpha=0.5)
axes[0].set_xlabel('预测值', fontsize=10)
axes[0].set_ylabel('残差', fontsize=10)
axes[0].set_title('残差 vs 预测值（方差齐性检验）', fontsize=11, fontweight='bold')
axes[0].legend(fontsize=8)
axes[0].grid(True, alpha=0.3)

# Q-Q图
from scipy import stats
stats.probplot(residuals, dist="norm", plot=axes[1])
axes[1].get_lines()[0].set_markerfacecolor('#2196F3')
axes[1].get_lines()[0].set_markeredgecolor('white')
axes[1].get_lines()[0].set_alpha(0.5)
axes[1].get_lines()[1].set_color('red')
axes[1].get_lines()[1].set_linestyle('--')
axes[1].set_title('残差 Q-Q 正态性检验', fontsize=11, fontweight='bold')

fig.suptitle('图5-4  残差诊断分析', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('output/charts/fig_residual_diagnosis.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_residual_diagnosis.png")

# ============================================================
# 10. 图9: SHAP特征重要性
# ============================================================
print("[9/10] Generating SHAP feature importance...")
fi = model_results.get('feature_importance', {})
fi_sorted = sorted(fi.items(), key=lambda x: x[1], reverse=True)[:15]
fi_names = [n for n, v in fi_sorted]
fi_vals = [v for n, v in fi_sorted]

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.barh(fi_names[::-1], fi_vals[::-1], color=['#1a237e' if 'temp_avg_roll3_std' in n else '#5c6bc0' if v > 0 else '#e0e0e0' for n, v in fi_sorted[::-1]])
ax.set_xlabel('SHAP重要性得分', fontsize=11)
ax.set_title('图5-5  LightGBM模型SHAP特征重要性排序（前15位）', fontsize=13, fontweight='bold')

# 标注非零特征
for bar, (name, val) in zip(bars, fi_sorted[::-1]):
    if val > 0:
        ax.text(val + 5, bar.get_y() + bar.get_height()/2, f'{val:.0f}',
                va='center', fontsize=8)

ax.grid(True, alpha=0.2, axis='x')
plt.tight_layout()
plt.savefig('output/charts/fig_shap_importance.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_shap_importance.png")

# ============================================================
# 11. 图10: 季节性热力图
# ============================================================
print("[10/10] Generating seasonal heatmap...")
disease_pivot = disease.pivot_table(values='incidence', index='district', columns='month', aggfunc='mean')

fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(disease_pivot.values, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(12))
ax.set_xticklabels([f'{m}月' for m in range(1, 13)], fontsize=9)
ax.set_yticks(range(len(disease_pivot.index)))
ax.set_yticklabels(disease_pivot.index, fontsize=9)

for i in range(len(disease_pivot.index)):
    for j in range(12):
        val = disease_pivot.values[i, j]
        if not np.isnan(val):
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', fontsize=7,
                    color='white' if val > np.nanmean(disease_pivot.values) else 'black')

cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('平均发病率 (每10万人)', fontsize=9)
ax.set_title('图4-2  北京市各行政区逐月流感发病率季节性热力图', fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig('output/charts/fig_seasonal_heatmap.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_seasonal_heatmap.png")

# ============================================================
# 图11: 系统架构图（文字版示意图）
# ============================================================
print("[Bonus] Generating system architecture diagram...")
fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis('off')

# 四层架构
layers = [
    ('展现层', 0, 5.5, 'Streamlit Web UI\n├ 首页仪表板\n├ 数据采集/管理\n├ 数据可视化\n├ 建模训练/评测\n├ 报告生成\n└ AI助手'),
    ('业务层', 0, 3.5, 'AgentPipeline 调度引擎\n├ CrawlAgent → CleanAgent\n├ FeatureEngineer\n├ ModelAgent → EvalAgent\n└ ReportAgent'),
    ('计算层', 0, 1.5, '核心算法\n├ 特征工程 (Lag/Rolling/OH)\n├ 10模型池 (LGB/XGB/RF/...)\n├ 7指标评测 + SHAP\n└ Jinja2 报告渲染'),
    ('数据层', 0, -0.5, '多源数据\n├ CMA 地面观测 ┄ 高空探空\n├ 天气网 ┄ 天气后报\n├ 北京市卫健委 ┄ CDC\n└ 文献数据提取'),
]
layer_colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']

for i, (name, x, y, desc) in enumerate(layers):
    # 层背景
    rect = plt.Rectangle((x, y), 12, 1.8, facecolor=layer_colors[i], alpha=0.15,
                          edgecolor=layer_colors[i], linewidth=2, linestyle='-')
    ax.add_patch(rect)
    # 层名称
    ax.text(x + 0.2, y + 1.55, name, fontsize=13, fontweight='bold', color=layer_colors[i], va='top')
    # 内容
    ax.text(x + 6, y + 0.9, desc, fontsize=8, ha='center', va='center',
            family='monospace', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

# 箭头
for i in range(3):
    y_from = 5.5 - i * 2
    y_to = 3.5 - i * 2
    ax.annotate('', xy=(6, y_to + 1.8), xytext=(6, y_from),
                arrowprops=dict(arrowstyle='->', color='#333', lw=2.5))

ax.set_title('图2-1  系统四层总体架构', fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('output/charts/fig_architecture.png', dpi=200, bbox_inches='tight')
plt.close()
print("  Done: fig_architecture.png")

# ============================================================
# Summary
# ============================================================
print("\n" + "="*60)
print("All 11 charts generated successfully!")
print(f"Output directory: {os.path.abspath('output/charts')}")
print("Files:")
for f in sorted(os.listdir('output/charts')):
    size_kb = os.path.getsize(f'output/charts/{f}') / 1024
    print(f"  {f} ({size_kb:.0f} KB)")
