"""用 PIL 直接绘制架构图 — 完全绕过 matplotlib 字体问题"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 2400, 1500
img = Image.new('RGB', (W, H), 'white')
draw = ImageDraw.Draw(img)

# 加载字体
font_path = "C:\\Windows\\Fonts\\simhei.ttf"
try:
    font_title = ImageFont.truetype(font_path, 42)
    font_layer = ImageFont.truetype(font_path, 36)
    font_body = ImageFont.truetype(font_path, 24)
    font_body_small = ImageFont.truetype(font_path, 22)
    print(f"字体加载成功: {font_path}")
except Exception as e:
    print(f"字体加载失败: {e}, 尝试备用字体...")
    font_path = "C:\\Windows\\Fonts\\msyh.ttc"
    font_title = ImageFont.truetype(font_path, 42)
    font_layer = ImageFont.truetype(font_path, 36)
    font_body = ImageFont.truetype(font_path, 24)
    font_body_small = ImageFont.truetype(font_path, 22)

# 颜色
colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']
colors_bg = [(102,126,234,30), (118,75,162,30), (240,147,251,30), (245,87,108,30)]

# 层定义
layers = [
    ('展现层', [
        'Streamlit Web 交互界面',
        '├ 首页仪表板              ├ 数据采集页面',
        '├ 数据管理页面            ├ 数据可视化页面',
        '├ 建模训练页面            ├ 模型评测页面',
        '├ 报告生成页面            └ AI 助手页面',
    ]),
    ('业务层', [
        'AgentPipeline 配置驱动调度引擎',
        '├ CrawlAgent      数据采集智能体',
        '├ CleanAgent      数据清洗智能体',
        '├ FeatureEngineer 特征工程',
        '├ ModelAgent      自适应建模智能体',
        '├ EvalAgent       模型评测智能体',
        '├ ReportAgent     报告生成智能体',
        '└ ProvenanceTracker  溯源追踪',
    ]),
    ('计算层', [
        '核心算法计算层',
        '├ 特征工程流水线（聚合 / 滞后 / 滑动窗 / 哑变量编码）',
        '├ 十模型池（LightGBM / XGBoost / 随机森林 / SVR 等）',
        '├ 七项指标评测 + 过拟合 / 欠拟合检测',
        '├ SHAP 可解释性分析 + 残差诊断',
        '└ Jinja2 模板引擎自动报告渲染',
    ]),
    ('数据层', [
        '多源异构数据接入层',
        '├ 国家气象信息中心 ─ 地面气象 + 高空探空观测',
        '├ 中国天气网 ─ 历史均值 / 实况 / 天气预报',
        '├ 天气后报网 ─ 历史气象实况数据',
        '├ 北京市卫健委 ─ 法定传染病疫情月报',
        '├ 中国疾控中心 ─ 全国传染病监测数据',
        '└ 文献数据 ─ PDF / Excel 格式化提取',
    ]),
]

# 布局参数
margin_top = 120
margin_bottom = 80
margin_left = 80
available_height = H - margin_top - margin_bottom
layer_h = available_height // 4
gap = 15

# 画标题
title = '图3-1  系统四层总体架构示意图'
bbox = draw.textbbox((0, 0), title, font=font_title)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, 30), title, fill='#222222', font=font_title)

# 画每层
for i, (name, lines) in enumerate(layers):
    y_top = margin_top + i * layer_h
    y_mid = y_top + layer_h // 2
    y_bottom = y_top + layer_h

    # 层背景矩形
    col = colors[i]
    # 解析颜色
    r, g, b = int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16)
    overlay = Image.new('RGBA', (W - 2 * margin_left, layer_h - gap), (r, g, b, 30))
    img.paste(overlay, (margin_left, y_top), overlay)

    # 边框
    draw.rectangle([margin_left, y_top, W - margin_left, y_bottom - gap],
                   outline=col, width=3)

    # 层标签
    draw.text((margin_left + 20, y_top + 12), name, fill=col, font=font_layer)

    # 层内容 — 在白底框中
    text_x = margin_left + 30
    text_y = y_top + 55
    # 白底框
    text_box_w = W - 2 * margin_left - 60
    text_box_h = layer_h - gap - 75
    draw.rectangle([text_x - 10, text_y - 8, text_x + text_box_w, text_y + text_box_h + 8],
                   fill='white', outline=col, width=1)

    # 画文字
    line_h = 32
    for j, line in enumerate(lines):
        y = text_y + j * line_h
        is_title_line = (j == 0)
        f = font_body if is_title_line else font_body_small
        c = '#333333' if is_title_line else '#555555'
        draw.text((text_x, y), line, fill=c, font=f)

    # 层间箭头
    if i < 3:
        arrow_y_from = y_bottom - gap
        arrow_y_to = y_bottom
        arrow_x = W // 2
        # 箭头线
        draw.line([(arrow_x, arrow_y_from), (arrow_x, arrow_y_to)],
                  fill='#333333', width=4)
        # 箭头三角
        pts = [(arrow_x - 12, arrow_y_to - 14), (arrow_x + 12, arrow_y_to - 14),
               (arrow_x, arrow_y_to + 5)]
        draw.polygon(pts, fill='#333333')

# 保存
out_path = 'output/charts/c3.png'
img.save(out_path, 'PNG')
print(f'架构图已生成: {out_path}')
print(f'尺寸: {W}x{H}')
print(f'文件大小: {os.path.getsize(out_path)/1024:.0f} KB')
