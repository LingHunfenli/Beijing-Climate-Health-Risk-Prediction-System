"""
修复版图片插入 — 使用纯 python-docx API，不碰 XML
策略：在文档末尾添加图片段落，然后用 lxml addnext 移动到目标位置
"""
import os
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from lxml import etree

INPUT_PATH = "北京市气候健康风险预警—智能体可视化平台_毕业论文.docx"
CHART_DIR = "output/charts"

# 先确保有干净的文档
print("Regenerating clean document...")
for script in ['generate_thesis.py', 'generate_thesis_p2.py', 'generate_thesis_p3.py',
               'generate_thesis_p4.py', 'generate_thesis_p5.py', 'generate_thesis_p6.py']:
    os.system(f'"C:\\Users\\34815\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" {script}')

doc = Document(INPUT_PATH)

def find_para(search_text, nth=1):
    """找到包含search_text的第nth个段落索引"""
    count = 0
    for i, p in enumerate(doc.paragraphs):
        if search_text in p.text:
            count += 1
            if count == nth:
                return i
    return None

def insert_image_after_para(para_idx, image_path, caption, width_inches=5.8):
    """
    在指定段落后面插入图片+题注。
    关键：不复制XML，直接在目标document中创建新段落，然后用addnext移动。
    """
    ref_para = doc.paragraphs[para_idx]

    # 先在文档末尾添加图片段落（安全的API操作）
    img_p = doc.add_paragraph()
    img_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_p.paragraph_format.first_line_indent = Cm(0)
    img_p.paragraph_format.space_before = Pt(6)
    img_p.paragraph_format.space_after = Pt(3)
    img_run = img_p.add_run()
    img_run.add_picture(image_path, width=Inches(width_inches))

    # 在文档末尾添加题注段落
    cap_p = doc.add_paragraph()
    cap_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_p.paragraph_format.first_line_indent = Cm(0)
    cap_p.paragraph_format.space_before = Pt(3)
    cap_p.paragraph_format.space_after = Pt(6)
    cap_run = cap_p.add_run(caption)
    cap_run.font.name = '宋体'
    cap_run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    cap_run.font.size = Pt(10.5)

    # 现在用XML操作将这两个段落移动到参考段落后面
    ref_elem = ref_para._element
    img_elem = img_p._element
    cap_elem = cap_p._element

    # 从文档末尾移除
    doc.element.body.remove(img_elem)
    doc.element.body.remove(cap_elem)

    # 移动到参考段落后（img在前，cap在后）
    ref_elem.addnext(cap_elem)  # 先加后面的
    ref_elem.addnext(img_elem)   # 再加前面的（变成: ref -> img -> cap）

    print(f"  ✓ {os.path.basename(image_path)} -> {caption[:60]}...")

# ============================================================
# 图片插入映射
# ============================================================
insertions = [
    ("3.1  系统总体架构设计", 1, f"{CHART_DIR}/fig_architecture.png",
     "图3-1  系统四层总体架构示意图", 5.5),
    ("3.4  特征工程模块设计", 1, f"{CHART_DIR}/fig_weather_timeseries.png",
     "图3-2  北京市主要行政区（海淀、朝阳、北京站）气象要素时序对比", 5.8),
    ("捕捉短期气象变化趋势和波动幅度。", 1, f"{CHART_DIR}/fig_correlation_heatmap.png",
     "图3-3  气象要素间皮尔逊相关系数热力图", 5.2),
    ("5.2  数据采集与清洗结果", 1, f"{CHART_DIR}/fig_disease_trend.png",
     "图5-1  北京市主要行政区流感发病率时序趋势", 5.8),
    ("5.2  数据采集与清洗结果", 2, f"{CHART_DIR}/fig_seasonal_heatmap.png",
     "图5-2  北京市各行政区逐月流感发病率季节性热力图", 5.6),
    ("5.3  特征工程与探索性数据分析", 1, f"{CHART_DIR}/fig_beijing_map.png",
     "图5-3  北京市各行政区平均气温空间分布", 5.2),
    ("从表5-1可以看出以下关键发现", 1, f"{CHART_DIR}/fig_model_ranking.png",
     "图5-4  十种机器学习模型性能对比（R²、RMSE、MAPE）", 5.8),
    ("泛化稳定性不如基于树的集成方法。", 1, f"{CHART_DIR}/fig_model_radar.png",
     "图5-5  最优五模型多维度雷达对比图", 5.0),
    ("5.5  模型可解释性分析", 1, f"{CHART_DIR}/fig_predicted_vs_actual.png",
     "图5-6  LightGBM模型预测值与实测发病率拟合散点图", 5.2),
    ("没有过度记忆训练数据的噪声。", 1, f"{CHART_DIR}/fig_residual_diagnosis.png",
     "图5-7  残差诊断分析（左：方差齐性检验，右：Q-Q正态性检验）", 5.8),
    ("SHAP特征重要性分析揭示了如下关键模式", 1, f"{CHART_DIR}/fig_shap_importance.png",
     "图5-8  LightGBM模型SHAP特征重要性排序（前15位）", 5.5),
]

for search, nth, img_path, caption, width in insertions:
    idx = find_para(search, nth)
    if idx is not None and os.path.exists(img_path):
        insert_image_after_para(idx, img_path, caption, width)
    else:
        print(f"  ✗ SKIP: text='{search[:40]}...' nth={nth} found={idx is not None} file={os.path.exists(img_path)}")

# 保存
doc.save(INPUT_PATH)
print(f"\nDone! Saved to: {INPUT_PATH}")
print("Open in Word to verify all images render correctly.")
