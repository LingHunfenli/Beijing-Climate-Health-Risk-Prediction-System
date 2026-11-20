"""PIL 架构图 v2 — 极简风格，纯色块 + 文字，零透明度"""
from PIL import Image, ImageDraw, ImageFont

W, H = 2400, 1400
img = Image.new('RGB', (W, H), '#FAFAFA')
draw = ImageDraw.Draw(img)

font_path = "C:\\Windows\\Fonts\\simhei.ttf"
f_title = ImageFont.truetype(font_path, 40)
f_label = ImageFont.truetype(font_path, 32)
f_text  = ImageFont.truetype(font_path, 22)

# ============ 标题 ============
title = '图3-1  系统四层总体架构示意图'
tw = draw.textlength(title, font=f_title)
draw.text(((W - tw) // 2, 25), title, fill='#1a1a1a', font=f_title)

# ============ 四个层的参数 ============
colors_fill = ['#E8EAF6', '#EDE7F6', '#FCE4EC', '#FFEBEE']
colors_stroke = ['#5C6BC0', '#7E57C2', '#EC407A', '#EF5350']
colors_text = ['#283593', '#4A148C', '#880E4F', '#B71C1C']
labels = ['展  现  层', '业  务  层', '计  算  层', '数  据  层']

content = [
    [
        'Streamlit Web 交互界面',
        '首页仪表板  |  数据采集  |  数据管理  |  数据可视化',
        '建模训练  |  模型评测  |  报告生成  |  AI 助手',
    ],
    [
        'AgentPipeline 配置驱动调度引擎',
        'CrawlAgent 数据采集  →  CleanAgent 数据清洗  →  FeatureEngineer 特征工程',
        'ModelAgent 建模训练  →  EvalAgent 模型评测  →  ReportAgent 报告生成',
        'ProvenanceTracker 溯源追踪（全程记录）',
    ],
    [
        '核心算法与计算模块',
        '特征工程流水线：日聚合 / 滞后特征 / 滑动窗 / 极端天气标记 / 月份哑变量',
        '模型池（10种）：LightGBM / XGBoost / 随机森林 / SVR / ElasticNet 等',
        '评测体系：R² / RMSE / MAPE / 过拟合检测 / SHAP 可解释性 / 残差诊断',
        '报告引擎：Jinja2 模板 → HTML / Markdown 综合报告',
    ],
    [
        '多源异构数据接入层',
        'CMA 国家气象信息中心：地面气象观测 + 高空探空观测',
        '中国天气网：历史均值 / 天气实况 / 40天预报',
        '北京市卫健委：法定传染病疫情月报    中国 CDC：全国传染病监测',
        '天气后报网：历史气象实况    文献数据：PDF / Excel 提取',
    ],
]

box_x0, box_x1 = 60, W - 60
box_w = box_x1 - box_x0
top_y = 90
box_h = 275
gap = 35

for i in range(4):
    y0 = top_y + i * (box_h + gap)
    y1 = y0 + box_h

    # 填充背景
    draw.rectangle([box_x0, y0, box_x1, y1], fill=colors_fill[i],
                   outline=colors_stroke[i], width=3)

    # 层标签（左侧竖排色块）
    tag_w = 110
    draw.rectangle([box_x0, y0, box_x0 + tag_w, y1],
                   fill=colors_stroke[i], outline=colors_stroke[i])

    # 标签文字（竖排效果：一个字一行）
    label = labels[i]
    for j, ch in enumerate(label):
        ch_w = draw.textlength(ch, font=f_label)
        ch_x = box_x0 + (tag_w - ch_w) // 2
        ch_y = y0 + 30 + j * 55
        draw.text((ch_x, ch_y), ch, fill='white', font=f_label)

    # 右侧内容文字
    cx = box_x0 + tag_w + 30
    cy = y0 + 18

    for j, line in enumerate(content[i]):
        if j == 0:
            draw.text((cx, cy), line, fill=colors_text[i], font=f_label)
            cy += 50
        else:
            draw.text((cx, cy), line, fill='#444444', font=f_text)
            cy += 38

    # 层间箭头
    if i < 3:
        arrow_y = y1 + 5
        arrow_tip_y = y1 + gap - 8
        arrow_x = W // 2
        draw.line([(arrow_x, arrow_y), (arrow_x, arrow_tip_y)],
                  fill='#555555', width=3)
        # 三角箭头
        sz = 12
        draw.polygon([(arrow_x - sz, arrow_tip_y - sz),
                       (arrow_x + sz, arrow_tip_y - sz),
                       (arrow_x, arrow_tip_y + 8)],
                      fill='#555555')

out = 'output/charts/c3.png'
img.save(out, 'PNG')
print(f'OK: {out}  ({W}x{H})')
