"""
将生成的图表插入论文文档
"""
import os
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

INPUT_PATH = "北京市气候健康风险预警—智能体可视化平台_毕业论文.docx"
CHART_DIR = "output/charts"

doc = Document(INPUT_PATH)

def find_para_after(doc, search_text, nth=1):
    """找到包含search_text的第nth个段落，返回其索引"""
    count = 0
    for i, p in enumerate(doc.paragraphs):
        if search_text in p.text:
            count += 1
            if count == nth:
                return i
    return None

def insert_image_after(doc, para_idx, image_path, caption, width_inches=5.8):
    """在指定段落索引之后插入图片和标题（通过XML操作）"""
    from docx.oxml.ns import qn as ns_qn
    from lxml import etree
    from copy import deepcopy

    # 获取参考段落
    ref_para = doc.paragraphs[para_idx]
    ref_elem = ref_para._element

    # 创建图片段落
    img_para_elem = deepcopy(ref_elem)  # 复制样式
    # 清空内容
    for child in list(img_para_elem):
        img_para_elem.remove(child)
    img_para_elem.clear()

    # 设置图片段落的属性
    pPr = img_para_elem.find(qn('w:pPr'))
    if pPr is None:
        pPr = etree.SubElement(img_para_elem, qn('w:pPr'))
    # 居中
    jc = pPr.find(qn('w:jc'))
    if jc is None:
        jc = etree.SubElement(pPr, qn('w:jc'))
    jc.set(qn('w:val'), 'center')
    # 首行缩进为0
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = etree.SubElement(pPr, qn('w:ind'))
    ind.set(qn('w:firstLine'), '0')
    ind.set(qn('w:left'), '0')

    # 添加图片run
    run_elem = etree.SubElement(img_para_elem, qn('w:r'))
    draw_elem = etree.SubElement(run_elem, qn('w:drawing'))

    # 创建图片的inline元素
    from docx.shared import Emu
    img_path = os.path.abspath(image_path)

    # 使用python-docx创建图片run来获取正确的XML
    tmp_doc = Document()
    tmp_p = tmp_doc.add_paragraph()
    tmp_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tmp_run = tmp_p.add_run()
    tmp_run.add_picture(img_path, width=Inches(width_inches))

    # 提取drawing元素
    tmp_drawing = tmp_p._element.find(qn('w:r')).find(qn('w:drawing'))
    if tmp_drawing is not None:
        run_elem.append(deepcopy(tmp_drawing))

    # 插入到参考段落后
    ref_elem.addnext(img_para_elem)

    # 创建题注段落
    cap_elem = deepcopy(img_para_elem)
    # 清除图片run
    cap_run = cap_elem.find(qn('w:r'))
    if cap_run is not None:
        cap_elem.remove(cap_run)
    # 清除drawing元素
    for d in cap_elem.findall('.//' + qn('w:drawing')):
        d.getparent().remove(d)

    # 添加题注文字
    cap_run_elem = etree.SubElement(cap_elem, qn('w:r'))
    rPr = etree.SubElement(cap_run_elem, qn('w:rPr'))
    rFonts = etree.SubElement(rPr, qn('w:rFonts'))
    rFonts.set(qn('w:ascii'), '宋体')
    rFonts.set(qn('w:eastAsia'), '宋体')
    sz = etree.SubElement(rPr, qn('w:sz'))
    sz.set(qn('w:val'), '21')  # 10.5pt = 21 half-points

    cap_text_elem = etree.SubElement(cap_run_elem, qn('w:t'))
    cap_text_elem.text = caption
    cap_text_elem.set(qn('xml:space'), 'preserve')

    # 题注段落到图片段落后面
    img_para_elem.addnext(cap_elem)

    print(f"  Inserted: {os.path.basename(image_path)} -> '{caption[:50]}...'")

# ============================================================
# Image insertion map
# ============================================================
insertions = [
    # (search_text, nth, image_path, caption, width)
    # 第3章: 架构图放在 3.1 系统总体架构设计 之后
    ("3.1  系统总体架构设计", 1,
     "output/charts/fig_architecture.png",
     "图3-1  系统四层总体架构示意图", 5.5),

    # 第3章: 气象要素时序图放在 3.4 特征工程之后
    ("3.4  特征工程模块设计", 1,
     "output/charts/fig_weather_timeseries.png",
     "图3-2  北京市主要行政区（海淀、朝阳、北京站）气象要素时序对比", 5.8),

    # 第3章: 相关性热力图
    ("捕捉短期气象变化趋势和波动幅度。", 1,
     "output/charts/fig_correlation_heatmap.png",
     "图3-3  气象要素间皮尔逊相关系数热力图", 5.2),

    # 第5章: 系统架构图已经放过，这里放疾病趋势图
    ("5.2  数据采集与清洗结果", 1,
     "output/charts/fig_disease_trend.png",
     "图5-1  北京市主要行政区流感发病率时序趋势", 5.8),

    # 第5章: 季节性热力图 — 放在含"季节"的段落
    ("5.2  数据采集与清洗结果", 2,
     "output/charts/fig_seasonal_heatmap.png",
     "图5-2  北京市各行政区逐月流感发病率季节性热力图", 5.6),

    # 第5章: 北京地图
    ("5.3  特征工程与探索性数据分析", 1,
     "output/charts/fig_beijing_map.png",
     "图5-3  北京市各行政区平均气温空间分布图", 5.2),

    # 第5章: 模型排名（table 5-1之后）
    ("从表5-1可以看出以下关键发现", 1,
     "output/charts/fig_model_ranking.png",
     "图5-4  十种机器学习模型性能对比（R²、RMSE、MAPE）", 5.8),

    # 第5章: 模型雷达图
    ("泛化稳定性不如基于树的集成方法。", 1,
     "output/charts/fig_model_radar.png",
     "图5-5  最优五模型多维度雷达对比图", 5.0),

    # 第5章: 拟合散点图
    ("5.5  模型可解释性分析", 1,
     "output/charts/fig_predicted_vs_actual.png",
     "图5-6  LightGBM模型预测值与实测发病率拟合散点图", 5.2),

    # 第5章: 残差诊断图
    ("没有过度记忆训练数据的噪声。", 1,
     "output/charts/fig_residual_diagnosis.png",
     "图5-7  残差诊断分析（左：方差齐性检验，右：Q-Q正态性检验）", 5.8),

    # 第5章: SHAP特征重要性 — 放在"SHAP特征重要性分析揭示"之后
    ("SHAP特征重要性分析揭示了如下关键模式", 1,
     "output/charts/fig_shap_importance.png",
     "图5-8  LightGBM模型SHAP特征重要性排序（前15位）", 5.5),
]

for search, nth, img_path, caption, width in insertions:
    idx = find_para_after(doc, search, nth)
    if idx is not None:
        if os.path.exists(img_path):
            insert_image_after(doc, idx, img_path, caption, width)
        else:
            print(f"  SKIP: Image not found: {img_path}")
    else:
        print(f"  SKIP: Text not found (nth={nth}): '{search[:50]}...'")

# ============================================================
# Save
# ============================================================
OUTPUT_PATH = "北京市气候健康风险预警—智能体可视化平台_毕业论文.docx"
doc.save(OUTPUT_PATH)
print(f"\nAll images inserted! Saved to: {OUTPUT_PATH}")
