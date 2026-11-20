"""
生成本科毕业设计（论文）— 北京市气候健康风险预警智能体可视化平台
严格遵循「本科毕业设计（论文）【模板】」格式要求
"""
import os
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import datetime

OUTPUT_PATH = "北京市气候健康风险预警—智能体可视化平台_毕业论文.docx"

doc = Document()

# ============================================================
# 全局样式设置
# ============================================================
style = doc.styles['Normal']
font = style.font
font.name = '宋体'
font.size = Pt(12)  # 小四号
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
style.paragraph_format.line_spacing = Pt(20)
style.paragraph_format.space_before = Pt(0)
style.paragraph_format.space_after = Pt(0)
style.paragraph_format.first_line_indent = Cm(0.74)  # 2个中文字符

# 页面设置
for section in doc.sections:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.5)

# 标题样式
for i in range(1, 4):
    heading = doc.styles[f'Heading {i}']
    heading.font.name = '黑体'
    heading.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    heading.font.color.rgb = RGBColor(0, 0, 0)
    heading.paragraph_format.line_spacing = Pt(20)
    heading.paragraph_format.first_line_indent = Cm(0)

h1 = doc.styles['Heading 1']
h1.font.size = Pt(16)  # 三号
h1.paragraph_format.space_before = Pt(18)
h1.paragraph_format.space_after = Pt(30)
h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

h2 = doc.styles['Heading 2']
h2.font.size = Pt(14)  # 四号
h2.paragraph_format.space_before = Pt(6)
h2.paragraph_format.space_after = Pt(6)

h3 = doc.styles['Heading 3']
h3.font.size = Pt(12)  # 小四号
h3.paragraph_format.space_before = Pt(6)
h3.paragraph_format.space_after = Pt(6)


def add_para(text, bold=False, alignment=None, font_name='宋体', font_size=Pt(12),
             first_line_indent=Cm(0.74), space_before=0, space_after=0, line_spacing=Pt(20)):
    """添加段落的便捷函数"""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.first_line_indent = first_line_indent
    if alignment is not None:
        p.paragraph_format.alignment = alignment
    run = p.add_run(text)
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = font_size
    run.bold = bold
    return p


def add_heading(text, level=1):
    """添加标题（自动分页）"""
    if level == 1:
        doc.add_page_break()
    h = doc.add_heading(text, level=level)
    return h


def add_figure_caption(text):
    """图标题：居中，5号宋体"""
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = Pt(20)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.font.name = '宋体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(10.5)  # 五号
    return p


def add_table_caption(text):
    """表标题：居中，5号宋体，位于表上方"""
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = Pt(20)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    run.font.name = '宋体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(10.5)  # 五号
    return p


# ============================================================
# 封面
# ============================================================

# 空行（模拟封面格式）
for _ in range(6):
    add_para("", first_line_indent=Cm(0), font_size=Pt(12))

add_para("本科生毕业设计(论文)", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER,
         font_name='黑体', font_size=Pt(22), first_line_indent=Cm(0), space_after=30)

add_para("北京市气候健康风险预警\n——智能体可视化平台的设计与实现", bold=True,
         alignment=WD_ALIGN_PARAGRAPH.CENTER, font_name='黑体', font_size=Pt(22),
         first_line_indent=Cm(0), space_after=60)

# 信息表格占位
info_lines = [
    "姓    名：________________________",
    "学    号：________________________",
    "学    院：数学与数据科学系",
    "专业(方向)：信息与计算科学",
    "班    级：________________________",
    "指导教师：何黎黎",
]
for line in info_lines:
    add_para(line, alignment=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent=Cm(0),
             font_size=Pt(14), font_name='宋体')

# 日期
add_para("", first_line_indent=Cm(0))
add_para(f"2026年7月", alignment=WD_ALIGN_PARAGRAPH.CENTER,
         first_line_indent=Cm(0), font_size=Pt(14))

# ============================================================
# 创见性声明（新页）
# ============================================================
doc.add_page_break()
add_heading("创见性声明", level=1)

add_para("本人声明：所呈交的毕业设计（论文）是本人在指导教师的指导下进行的工作和取得的成果，"
         "符合学校及学院的毕业设计（论文）管理规定，论文中所引用的他人已经发表或撰写过的研究成果，"
         "均加以特别标注并在此表示致谢。与我一同工作的同志对本论文所做的任何贡献也已在论文中作了"
         "明确的说明并表示谢意。", first_line_indent=Cm(0.74))

add_para("")
add_para("")
add_para("毕业论文作者签名：         签字日期：     年  月  日", first_line_indent=Cm(0))

# ============================================================
# 版权使用授权书（新页）
# ============================================================
doc.add_page_break()
add_heading("本科毕业设计（论文）版权使用授权书", level=1)

add_para("本毕业设计（论文）作者完全了解北京建筑大学有关保留、使用毕业设计（论文）的规定。"
         "特授权北京建筑大学可以将毕业设计（论文）的全部或部分内容编入有关数据库进行检索，"
         "并采用影印、缩印或扫描等复制手段保存、汇编以供查阅和借阅。同意学校向国家有关部门"
         "或机构送交毕业设计（论文）的复印件和磁盘。")
add_para("（保密的毕业论文在解密后适用本授权说明）")
add_para("")
add_para("")
add_para("毕业论文作者签名：           指导教师签名：", first_line_indent=Cm(0))
add_para("")
add_para("签字日期：     年  月  日    签字日期：    年  月  日", first_line_indent=Cm(0))

print("封面/声明部分完成...")

# ============================================================
# 中文摘要（新页）
# ============================================================
doc.add_page_break()
add_para("", first_line_indent=Cm(0))
add_para("摘    要", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER,
         font_name='黑体', font_size=Pt(16), first_line_indent=Cm(0),
         space_before=18, space_after=30, line_spacing=Pt(20))

abstract_cn = (
    "在全球气候变化的背景下，极端天气事件频发，气候因素对人体健康的影响日益显著。"
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
    "一套高效、可扩展的技术解决方案。"
)

add_para(abstract_cn, first_line_indent=Cm(0.74))

add_para("")
add_para("关键词：气候健康；风险预警；机器学习；智能体；数据可视化",
         bold=False, font_name='宋体', font_size=Pt(12), first_line_indent=Cm(0.74))

print("中文摘要完成...")

# ============================================================
# 英文摘要（新页）
# ============================================================
doc.add_page_break()
add_para("", first_line_indent=Cm(0))
add_para("ABSTRACT", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER,
         font_name='Times New Roman', font_size=Pt(16), first_line_indent=Cm(0),
         space_before=18, space_after=30)

abstract_en = (
    "Against the backdrop of global climate change, extreme weather events occur frequently, "
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
    "and scalable technical solution for climate-sensitive disease risk early warning in Beijing."
)

add_para(abstract_en, font_name='Times New Roman', font_size=Pt(12),
         first_line_indent=Cm(0.74))

add_para("")
add_para("Key Words: climate health; risk early warning; machine learning; intelligent agent; "
         "data visualization", font_name='Times New Roman', font_size=Pt(12),
         first_line_indent=Cm(0.74))

print("英文摘要完成...")

# ============================================================
# 目录页
# ============================================================
doc.add_page_break()
add_para("目    录", bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER,
         font_name='黑体', font_size=Pt(16), first_line_indent=Cm(0),
         space_before=18, space_after=30)

toc_items = [
    ("1  绪论", 1),
    ("  1.1  研究背景与意义", 2),
    ("  1.2  国内外研究现状", 2),
    ("  1.3  研究目标与内容", 2),
    ("  1.4  论文组织结构", 2),
    ("2  相关技术与理论基础", 1),
    ("  2.1  气象数据采集技术", 2),
    ("  2.2  数据清洗与质控方法", 2),
    ("  2.3  机器学习相关算法", 2),
    ("  2.4  智能体技术概述", 2),
    ("3  系统设计与架构", 1),
    ("  3.1  系统总体架构设计", 2),
    ("  3.2  数据采集模块设计", 2),
    ("  3.3  数据清洗与质控模块设计", 2),
    ("  3.4  特征工程模块设计", 2),
    ("  3.5  多模型自适应建模模块设计", 2),
    ("  3.6  模型评测与诊断模块设计", 2),
    ("  3.7  可视化与报告模块设计", 2),
    ("4  系统实现与关键技术", 1),
    ("  4.1  多源气象数据采集实现", 2),
    ("  4.2  自适应数据清洗与质控实现", 2),
    ("  4.3  特征工程与数据预处理实现", 2),
    ("  4.4  多模型自适应建模实现", 2),
    ("  4.5  全维度模型评测实现", 2),
    ("  4.6  智能体全流程自动化实现", 2),
    ("  4.7  AI助手与报告生成实现", 2),
    ("5  实验结果与分析", 1),
    ("  5.1  实验环境与数据说明", 2),
    ("  5.2  数据采集与清洗结果", 2),
    ("  5.3  特征工程与探索性数据分析", 2),
    ("  5.4  模型对比实验结果", 2),
    ("  5.5  模型可解释性分析", 2),
    ("  5.6  系统运行效果展示", 2),
    ("结论", 1),
    ("参考文献", 1),
    ("附录A  程序清单", 1),
    ("致谢", 1),
]

for item_text, level in toc_items:
    font_s = '黑体' if level == 1 else '宋体'
    font_size = Pt(12) if level == 1 else Pt(12)
    indent = Cm(0) if level == 1 else Cm(0.74)
    add_para(item_text, font_name=font_s, font_size=font_size,
             first_line_indent=indent, bold=(level == 1))

print("目录完成...")
doc.save(OUTPUT_PATH)
print(f"第1部分已保存至 {OUTPUT_PATH}")
