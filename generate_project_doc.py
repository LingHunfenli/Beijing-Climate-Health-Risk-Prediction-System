"""
生成项目详细说明 Word 文档
北京市气候健康风险预警 — 智能体可视化平台
"""
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
from datetime import datetime

doc = Document()

# ============================================================
# 样式设置
# ============================================================
style = doc.styles['Normal']
font = style.font
font.name = '微软雅黑'
font.size = Pt(11)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')

# 标题样式
for i in range(1, 4):
    heading_style = doc.styles[f'Heading {i}']
    heading_style.font.name = '微软雅黑'
    heading_style.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    if i == 1:
        heading_style.font.size = Pt(22)
        heading_style.font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)
    elif i == 2:
        heading_style.font.size = Pt(16)
        heading_style.font.color.rgb = RGBColor(0x2a, 0x5c, 0x8e)
    else:
        heading_style.font.size = Pt(13)
        heading_style.font.color.rgb = RGBColor(0x3a, 0x7c, 0xae)

def add_table(doc, headers, rows, col_widths=None):
    """添加格式化表格"""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # 表头
    for j, h in enumerate(headers):
        cell = table.rows[0].cells[j]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(10)

    # 数据行
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.rows[i + 1].cells[j]
            cell.text = str(val)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(10)

    doc.add_paragraph()
    return table

def add_code_block(doc, code_text):
    """添加代码块"""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1)
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    return p

def add_note(doc, text, note_type="info"):
    """添加提示框"""
    p = doc.add_paragraph()
    if note_type == "warning":
        prefix = "⚠️ 注意："
    elif note_type == "tip":
        prefix = "💡 提示："
    else:
        prefix = "📌 "
    run = p.add_run(prefix + text)
    run.font.size = Pt(10)
    run.font.italic = True
    if note_type == "warning":
        run.font.color.rgb = RGBColor(0xcc, 0x55, 0x00)
    return p

# ============================================================
# 封面
# ============================================================
for _ in range(6):
    doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('北京市气候健康风险预警')
run.font.size = Pt(32)
run.font.bold = True
run.font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('智能体可视化平台 — 项目详细说明')
run.font.size = Pt(20)
run.font.color.rgb = RGBColor(0x4a, 0x7c, 0xae)

doc.add_paragraph()

info = doc.add_paragraph()
info.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = info.add_run(f'版本：v2.1  |  生成日期：{datetime.now().strftime("%Y-%m-%d")}')
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

info2 = doc.add_paragraph()
info2.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = info2.add_run('技术栈：Python 3.13 + Streamlit + scikit-learn + XGBoost + Pyecharts')
run.font.size = Pt(11)
run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

doc.add_page_break()

# ============================================================
# 目录页
# ============================================================
doc.add_heading('目  录', level=1)
toc_items = [
    ('一、项目概述', '项目定位、核心目标、技术栈选型'),
    ('二、系统架构设计', '整体架构、AgentPipeline 调度引擎、数据流'),
    ('三、数据采集管线', '七个数据源详解、爬虫模块、信任度体系'),
    ('四、数据清洗与质控', '自适应清洗策略、哨兵值处理、质控报告'),
    ('五、特征工程', '日聚合、衍生特征、数据划分策略'),
    ('六、建模训练体系', 'AutoML 自适应决策树、10模型池、超参数搜索'),
    ('七、模型评测与可解释性', '全维度指标、残差诊断、SHAP 解释'),
    ('八、报告生成系统', 'Jinja2 模板、7章报告、ZIP 打包'),
    ('九、Web 可视化平台', 'Streamlit 6功能页、10种图表、AI 助手'),
    ('十、数据接口契约', '标准化 Schema、信任度体系、溯源系统'),
    ('十一、配置与运行指南', 'config.yaml、启动命令、命令行工具'),
    ('十二、质量保证体系', '自动核验脚本、数据真实性保障、已知限制'),
    ('附录', '文件结构树、产出文件速查、快速命令速查'),
]
for title_text, desc in toc_items:
    p = doc.add_paragraph()
    run = p.add_run(title_text)
    run.bold = True
    run.font.size = Pt(12)
    p2 = doc.add_paragraph()
    p2.paragraph_format.left_indent = Cm(1)
    run2 = p2.add_run(desc)
    run2.font.size = Pt(10)
    run2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

doc.add_page_break()

# ============================================================
# 一、项目概述
# ============================================================
doc.add_heading('一、项目概述', level=1)

doc.add_heading('1.1 项目定位', level=2)
doc.add_paragraph(
    '本项目是一个面向北京市气候健康风险预警的全流程自动化智能体平台。'
    '系统覆盖"数据采集 → 清洗质控 → 特征工程 → 自适应建模 → 多维度评测 → 报告生成"'
    '的完整分析管线。用户通过 Web UI 配置参数后一键启动，智能体自动执行，'
    '仅在数据异常或模型失效时触发人工复核介入。'
)

doc.add_heading('1.2 应用场景', level=2)
doc.add_paragraph(
    '气候变化与人群健康的关系日益受到关注。北京市作为超大城市，'
    '极端天气事件（热浪、寒潮、暴雨等）对传染病发病率、慢性病急性发作等'
    '均存在显著影响。本平台通过整合多源气象观测数据与公共卫生数据，'
    '构建气候-健康关联模型，为公共卫生决策提供数据支撑和预警能力。'
)

doc.add_heading('1.3 技术栈', level=2)
add_table(doc,
    ['层级', '技术选型', '说明'],
    [
        ['Web 界面', 'Streamlit', '单进程全栈框架，6 个功能页面，纯 Python 开发'],
        ['数据处理', 'Pandas + NumPy', '数据清洗、聚合、变换的核心工具'],
        ['可视化', 'Pyecharts + Plotly + Matplotlib', '地图/热力/时序/3D散点/SHAP/残差诊断共10种图表'],
        ['机器学习', 'scikit-learn + XGBoost + LightGBM', '10 模型池 + PyCaret 降级模式'],
        ['可解释性', 'SHAP', 'TreeExplainer → Linear → Kernel 回退链'],
        ['调度引擎', '自定义 AgentPipeline', 'YAML 驱动，6 步顺序执行 + 异常暂停'],
        ['报告生成', 'Jinja2 → HTML/Markdown', '7 章完整报告 + ZIP 打包下载'],
        ['配置管理', 'YAML (PyYAML)', '人类可读写，管道参数集中管理'],
    ]
)

doc.add_heading('1.4 项目规模', level=2)
add_table(doc,
    ['指标', '数值'],
    [
        ['Python 源文件', '30+ 个（含 7 个独立爬虫、5 个智能体、6 个 Streamlit 页面）'],
        ['数据源', '7 个（CMA 地面+高空、天气网、天气后报网、卫健委、CDC、文献）'],
        ['支持行政区', '北京 18 个区（顺义、海淀、延庆、密云、怀柔、平谷、通州、朝阳、昌平、门头沟、石景山、丰台、大兴、房山、北京等）'],
        ['气象记录', '882 条地面观测 + 249 条高空探空（Phase 1 原始数据）'],
        ['疾病数据', '13 个月北京市法定传染病月报数据'],
        ['模型池', '10 个回归模型（含 Linear、Ridge、Lasso、RF、GBDT、XGBoost、LightGBM、SVR、KNN 等）'],
    ]
)

doc.add_page_break()

# ============================================================
# 二、系统架构设计
# ============================================================
doc.add_heading('二、系统架构设计', level=1)

doc.add_heading('2.1 整体架构', level=2)
doc.add_paragraph(
    '系统采用分层架构设计，自底向上分为数据层、智能体层、调度层和展示层四个层次：'
)

add_table(doc,
    ['层次', '组件', '职责'],
    [
        ['展示层 (Web UI)', 'Streamlit App (app.py + 6 pages)', '用户交互、参数配置、图表渲染、报告下载'],
        ['调度层 (Pipeline)', 'AgentPipeline (agent/pipeline.py)', 'YAML驱动全流程编排、异常暂停、进度回调'],
        ['智能体层 (Agents)', '5 个 Agent + FeatureEngineer', '采集/清洗/建模/评测/报告，各司其职'],
        ['数据层 (Crawlers)', '7 个独立爬虫 + data_scripts', '多源数据获取、标准化输出、编码修复'],
    ]
)

doc.add_heading('2.2 AgentPipeline 调度引擎', level=2)
doc.add_paragraph(
    'AgentPipeline 是系统的核心调度引擎，定义在 agent/pipeline.py 中。'
    '它按固定顺序执行 6 个步骤，每步返回 (status, data, anomalies) 三元组。'
    '当 anomalies 非空时自动暂停，等待人工复核后再继续。'
)

doc.add_paragraph('执行流程：')
steps_desc = [
    ('Step 1 — CrawlAgent', '多源数据采集：检测已有 CSV 文件，记录溯源信息，注册数据来源与信任度'),
    ('Step 2 — CleanAgent', '自适应清洗质控：缺失值统计、IQR 异常值检测、生成质控报告'),
    ('Step 3 — FeatureEngineer', '特征工程：日聚合（3小时→日粒度）、衍生特征构造、训练/测试集划分'),
    ('Step 4 — ModelAgent', '模型训练：多模型并行训练、特征重要性排序、最佳模型保存'),
    ('Step 5 — EvalAgent', '模型评测：全维度指标计算、残差分析、过拟合/欠拟合诊断、SHAP 可解释性'),
    ('Step 6 — ReportAgent', '报告生成：Jinja2 模板渲染、图表嵌入、HTML/Markdown 输出、ZIP 打包'),
]
for step, desc in steps_desc:
    p = doc.add_paragraph()
    run = p.add_run(f'{step}：')
    run.bold = True
    p.add_run(desc)

doc.add_heading('2.3 异常处理机制', level=2)
doc.add_paragraph(
    '管线内置了完善的异常处理与人工复核机制：'
)
items = [
    '数据源全部失败 → 提示用户手动上传数据文件',
    '缺失率超过 50% → 建议排除该行政区',
    '模型 R² < 0 → 提示特征不足或数据量不足',
    '异常值超过 10% → 提示用户确认数据质量',
    '过拟合（Train R² - Test R² > 0.1）→ 发出过拟合警告',
    '欠拟合（两者 R² 均 < 0.5）→ 发出欠拟合警告',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ============================================================
# 三、数据采集管线
# ============================================================
doc.add_heading('三、数据采集管线', level=1)

doc.add_heading('3.1 数据源总览', level=2)
doc.add_paragraph(
    '平台整合了 7 个独立数据源，覆盖气象观测和公共卫生两大领域。'
    '每个数据源由独立的爬虫/采集器模块负责，通过统一的接口契约输出标准化数据。'
)

add_table(doc,
    ['数据源', '模块文件', '数据类型', '信任度', '状态'],
    [
        ['CMA 地面气象观测', 'Phase 1 原始数据 (SURF_CHN_MUL_HOR)', '18站 × 7天 × 8时次/天 = 882行', '5 (最高)', '✅ 已有'],
        ['CMA 高空气象探测', 'Phase 1 原始数据 (UPAR_GLB_MUL_FTM)', '1站 × 7天 × 2探空/天 ≈ 249行', '5 (最高)', '✅ 已有'],
        ['中国天气网 40天 API', 'agent/crawlers/weather_history.py', '~120行/月逐日气温', '2~3', '✅ 可用'],
        ['天气后报网', 'agent/crawlers/tianqihoubao.py', '~30行/月历史实况', '3', '✅ 可用'],
        ['CMA 数据门户', 'agent/crawlers/cma_portal.py', '取决于注册状态', '5', '⚠️ 需注册'],
        ['北京市卫健委', 'agent/crawlers/beijing_health_data.py', '13个月报，传染病数据', '3~4', '✅ 可用'],
        ['中国 CDC', 'agent/crawlers/china_cdc.py', '39种法定传染病分病种', '4', '⚠️ 有反爬'],
        ['文献数据提取', 'agent/crawlers/literature_extract.py', 'PDF/Excel 表格提取', '1', '✅ 可用'],
    ]
)

doc.add_heading('3.2 CMA 地面气象数据详解', level=2)
doc.add_paragraph(
    '地面气象观测数据是平台的建模核心数据。数据来源于国家气象信息中心（CMA），'
    '覆盖北京市 18 个气象台站，时间范围为 2026-07-05 至 2026-07-11（7天），'
    '观测频率为每 3 小时一次（每日 8 时次：0/3/6/9/12/15/18/21 北京时间）。'
)
doc.add_paragraph('核心字段包括：')
ground_fields = [
    '气压体系（4项）：本站气压、海平面气压、最高气压、最低气压',
    '风体系（6项）：最大风速、极大风速、极大风速风向、2分钟平均风向、2分钟平均风速、最大风速风向',
    '温度体系（3项）：气温、最高气温、最低气温',
    '湿度体系（2项）：相对湿度、最小相对湿度',
    '降水（1项）：过去3小时累计降水量',
]
for f in ground_fields:
    doc.add_paragraph(f, style='List Bullet')

add_note(doc, '海平面气压（PRS_Sea）字段含大量 999.x 哨兵值，建模时应自行决定是否剔除或作为缺失值处理。', 'warning')

doc.add_heading('3.3 CMA 高空气象数据详解', level=2)
doc.add_paragraph(
    '高空气象数据来自北京 54511 站（北京观象台）的探空观测，'
    '每日 2 次（00 和 12 世界时）释放探空气球，获取从地面到约 30km 高空的'
    '温度、风、湿度垂直剖面。数据包含 19 个气压层（地面层 + 18 个标准气压层：'
    '1000, 925, 850, 700, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 20, 10, 7, 5, 3 hPa）。'
)

add_note(doc, '严禁将高空气象数据与地面数据混合。例如 500hPa 层的 -18°C 与地面 +27°C 不能放在同一个"温度"列取平均。两者物理含义完全不同，应在建模中分开处理或作为不同特征输入。', 'warning')

doc.add_heading('3.4 天气网爬虫策略', level=2)
doc.add_paragraph(
    '天气网爬虫（weather_history.py）通过以下策略获取北京逐日气温数据：'
)
items = [
    '日历 API（calendar_new）：获取历史气温均值数据',
    '7 天预报 HTML 解析：获取近期预报值',
    '15/40 天预报 HTML 解析：获取中长期预报值',
    '三种数据类型（实况 > 预报 > 历史均值）按优先级去重合并',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')
add_note(doc, '天气网日历历史 API 已封锁（返回 404），当前获取的数据主要为预报值。预报数据在标准化流程中标记为 trust=-1，不入建模训练，仅作为趋势参考。', 'warning')

doc.add_heading('3.5 疾病数据采集', level=2)
doc.add_paragraph(
    '疾病数据通过 beijing_health_data.py 综合采集器获取，覆盖三个来源：'
)
items = [
    '源1 — 北京市卫健委 (wjw.beijing.gov.cn)：月度法定传染病报告，提取总病例数 + 死亡数 + 主要病种',
    '源2 — 北京疾控中心 (bjcdc.org.cn)：SSL 证书问题，作为备用渠道',
    '源3 — 公共卫生科学数据中心 (phsciencedata.cn)：公开数据集下载',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ============================================================
# 四、数据清洗与质控
# ============================================================
doc.add_heading('四、数据清洗与质控', level=1)

doc.add_heading('4.1 哨兵值处理', level=2)
doc.add_paragraph(
    'CMA 原始数据中使用特定数值表示缺失或无效观测（哨兵值）。'
    '清洗脚本自动识别并处理以下哨兵值：'
)
add_table(doc,
    ['哨兵值', '含义', '处理方式', '影响字段'],
    [
        ['999017', '静风/风向不定', '替换为 NaN', '极大风速风向、2分钟平均风向、最大风速风向'],
        ['999990', '降水量缺失', '替换为 NaN', '过去3小时降水量'],
        ['999.x', '海平面气压系统性缺失', '保留原值（无法100%确认）', '海平面气压 (PRS_Sea)'],
    ]
)

doc.add_heading('4.2 自适应清洗策略', level=2)
doc.add_paragraph(
    'CleanAgent（agent/agents/clean_agent.py）实现了自适应清洗策略：'
)
items = [
    '缺失值统计：逐列计算缺失数量和缺失率，标记缺失率 > 50% 的列',
    'IQR 异常值检测：对数值型列使用 1.5×IQR 规则检测异常值',
    '物理范围校验：温度 [-50, 55]℃、湿度 [0, 100]%、气压 [850, 1100] hPa',
    '高空温度递减校验：地面温度必须 > 高层温度（验证气象物理规律）',
    '自动生成质控报告（Markdown 格式），包含 6 个章节的详细分析',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('4.3 Excel 兼容性处理', level=2)
doc.add_paragraph(
    '为确保数据在 Excel/WPS 中正确显示（尤其是中文和日期格式），'
    '所有输出 CSV 均经过 make_excel_ready.py 处理：'
)
add_table(doc,
    ['处理项', '方式', '目的'],
    [
        ['UTF-8 BOM', '文件头部添加 \\xef\\xbb\\xbf', 'Excel 正确识别中文编码'],
        ['CRLF 行尾', '\\r\\n 行尾符', 'Windows 标准行尾'],
        ['日期保护', '="YYYY-MM-DD" 格式', '防止 Excel 自动转换日期格式'],
        ['ID 保护', '="区站号" 格式', '防止前导零丢失（如 54511 不被转为 54511）'],
    ]
)

doc.add_page_break()

# ============================================================
# 五、特征工程
# ============================================================
doc.add_heading('五、特征工程', level=1)

doc.add_heading('5.1 日聚合', level=2)
doc.add_paragraph(
    '原始地面观测数据为 3 小时间隔（每站每日 8 时次），'
    '为匹配疾病数据的月度粒度，需先聚合为日粒度：'
)
items = [
    '温度：取日均值 (temp_avg)、日最高 (temp_max)、日最低 (temp_min)',
    '湿度：取日均值 (humidity_avg)',
    '气压：取日均值 (pressure_avg)',
    '风速：取日均值 (wind_speed_avg)',
    '降水：取日累计 (precipitation)',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('5.2 衍生特征', level=2)
doc.add_paragraph(
    'FeatureEngineer（agent/features.py）在日聚合基础上构造衍生特征：'
)
items = [
    '温度日较差（temp_max - temp_min）',
    '连续高温天数（rolling count）',
    '温湿指数（THI，综合衡量体感舒适度）',
    '滞后特征（lag-1, lag-2, lag-3 的发病率/气象变量）',
    '滑动窗口统计（3日/7日均值、标准差）',
    '季节性虚拟变量（月份 one-hot）',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('5.3 数据划分', level=2)
doc.add_paragraph(
    '训练/测试集按照 config.yaml 中配置的 test_size 比例（默认 20%）划分，'
    '支持 K-Fold 交叉验证（默认 5 折）。划分前自动排除 trust=-1 的预报数据。'
    '当样本量不足 50 条时，系统自动降级为仅使用线性回归模型并标注"仅供参考"。'
)

doc.add_page_break()

# ============================================================
# 六、建模训练体系
# ============================================================
doc.add_heading('六、建模训练体系', level=1)

doc.add_heading('6.1 AutoML 自适应决策树', level=2)
doc.add_paragraph(
    'ModelAgent 内置了自适应决策逻辑，根据数据量自动选择最佳建模策略：'
)
add_table(doc,
    ['数据量', '策略', '模型池'],
    [
        ['< 50 行', '仅线性回归，标注"模型仅供参考"', 'LinearRegression'],
        ['50-200 行', '基础模型池，无 CV', 'Linear + Ridge + Lasso + DecisionTree'],
        ['200-1000 行', '全模型池 + 5-Fold CV + RFE 特征筛选', '全部 10 个模型'],
        ['> 1000 行', '全模型池 + 10-Fold CV + 全超参数搜索', '全部 10 个模型 + GridSearchCV'],
    ]
)

doc.add_heading('6.2 模型池', level=2)
doc.add_paragraph('系统内置的 10 模型池如下：')
models_list = [
    'LinearRegression — 最小二乘线性回归（基准模型）',
    'Ridge — L2 正则化线性回归（α=1.0）',
    'Lasso — L1 正则化线性回归（α=0.1，自动特征选择）',
    'RandomForestRegressor — 随机森林（n_estimators=100）',
    'GradientBoostingRegressor — 梯度提升树（n_estimators=100）',
    'XGBoost — 极端梯度提升（需安装 xgboost 包）',
    'LightGBM — 轻量梯度提升（需安装 lightgbm 包）',
    'SVR — 支持向量回归（RBF 核）',
    'KNeighborsRegressor — K 近邻回归（k=5）',
    'DecisionTreeRegressor — 决策树回归',
]
for m in models_list:
    doc.add_paragraph(m, style='List Bullet')

doc.add_heading('6.3 PyCaret 降级模式', level=2)
doc.add_paragraph(
    '系统优先尝试使用 PyCaret 自动化机器学习库进行模型训练。'
    '当 PyCaret 不可用时（未安装或导入失败），自动降级为 sklearn 原生实现，'
    '包括手动模型逐一训练、GridSearchCV 超参数搜索、交叉验证等。'
    '两种模式功能等价，不影响建模效果。'
)

doc.add_heading('6.4 模型保存', level=2)
doc.add_paragraph(
    '训练完成后，最佳模型自动保存到 models/ 目录：'
)
items = [
    'models/best_model.pkl — sklearn 兼容 pickle 格式，可直接加载使用',
    'models/model_ranking.json — 所有模型的完整指标排名、特征重要性、诊断结论',
    'models/feature_config.json — 特征列表、目标变量名、划分参数',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ============================================================
# 七、模型评测与可解释性
# ============================================================
doc.add_heading('七、模型评测与可解释性', level=1)

doc.add_heading('7.1 全维度指标', level=2)
doc.add_paragraph(
    'EvalAgent 针对最优模型和全部对比模型提供多维度的评测指标：'
)
add_table(doc,
    ['类别', '指标', '说明'],
    [
        ['拟合精度', 'MAE, MSE, RMSE, R², Adjusted R²', '标准回归模型评估指标'],
        ['百分比误差', 'MAPE, SMAPE', '排除 y=0 的情况，衡量相对误差'],
        ['极端误差', 'Max Error, Median Absolute Error', '评估最坏情况下的预测表现'],
        ['残差正态性', 'Shapiro-Wilk 检验', '检验残差是否服从正态分布（线性回归假设）'],
        ['异方差检验', 'Breusch-Pagan 检验', '检测残差方差是否恒定'],
        ['泛化能力', 'K-Fold CV R² (mean±std), Learning Curve', '检测过拟合/欠拟合'],
        ['模型对比', '雷达图 + 排名条形图', '多模型多维直观比较'],
    ]
)

doc.add_heading('7.2 自动诊断规则', level=2)
add_table(doc,
    ['诊断', '条件', '含义'],
    [
        ['⚠️ 过拟合', 'Train R² - Test R² > 0.1', '模型过于复杂，泛化能力不足，建议增加正则化或减少特征'],
        ['⚠️ 欠拟合', 'Train R² + Test R² 均 < 0.5', '模型未能捕捉数据规律，建议增加特征或使用更复杂模型'],
        ['✅ 正常', '上述条件均不满足', '模型拟合良好，泛化能力可接受'],
    ]
)

doc.add_heading('7.3 SHAP 可解释性', level=2)
doc.add_paragraph(
    '平台集成 SHAP（SHapley Additive exPlanations）进行模型解释，'
    '采用三级回退链确保在各种模型类型下都能工作：'
)
items = [
    'TreeExplainer → 适用于树模型（RF、GBDT、XGBoost、LightGBM），速度最快',
    'LinearExplainer → 适用于线性模型（Ridge、Lasso、LinearRegression）',
    'KernelExplainer → 通用回退方案，适用于 SVR、KNN 等任意黑盒模型',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')
doc.add_paragraph(
    'SHAP 输出包括：特征重要性排序条形图、每个特征的 SHAP 依赖图、'
    '单个预测的 SHAP 力图（瀑布图）等，帮助理解模型决策逻辑。'
)

doc.add_page_break()

# ============================================================
# 八、报告生成系统
# ============================================================
doc.add_heading('八、报告生成系统', level=1)

doc.add_heading('8.1 报告模板', level=2)
doc.add_paragraph(
    '报告使用 Jinja2 模板引擎渲染，模板文件位于 templates/report.md.j2。'
    '模板定义了 7 个章节的结构和样式，支持嵌入图片、表格、代码块等丰富内容。'
)

doc.add_heading('8.2 报告内容', level=2)
add_table(doc,
    ['章节', '内容', '数据来源'],
    [
        ['一、数据概况', '气象/疾病数据统计摘要（行数、站数、时间范围）', 'CleanAgent 输出'],
        ['二、数据质控', '缺失率、哨兵值处理记录、异常值统计', '质控报告'],
        ['三、特征工程', '构造逻辑说明、特征重要性预排名', 'FeatureEngineer 输出'],
        ['四、模型结果', '最优模型参数、多模型对比排名表', 'ModelAgent 输出'],
        ['五、模型评测', '全指标表、诊断结论、残差分布图', 'EvalAgent 输出'],
        ['六、可视化', '内嵌图表（SHAP、热力图、趋势图、地图）', 'Visualizer 输出'],
        ['七、数据溯源', '每条数据来源URL、获取时间、信任度', 'ProvenanceTracker'],
    ]
)

doc.add_heading('8.3 输出格式', level=2)
doc.add_paragraph('报告支持多种输出格式：')
items = [
    'HTML — 完整网页格式，支持交互式图表（Plotly 图表可缩放/悬停）',
    'Markdown — 纯文本格式，便于版本管理和二次编辑',
    'ZIP 打包 — 包含 HTML 报告 + 数据集 CSV + 模型文件 + PNG 图表的全量包',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ============================================================
# 九、Web 可视化平台
# ============================================================
doc.add_heading('九、Web 可视化平台', level=1)

doc.add_heading('9.1 技术选型', level=2)
doc.add_paragraph(
    'Web 平台使用 Streamlit 构建。Streamlit 是一个纯 Python 的 Web 框架，'
    '无需 HTML/CSS/JavaScript 知识即可快速构建数据应用。'
    '其单进程全栈架构适合数据科学项目的快速迭代和部署。'
)
doc.add_paragraph('启动命令：streamlit run app.py（默认端口 8501）')

doc.add_heading('9.2 功能页面', level=2)
add_table(doc,
    ['页面', '文件', '功能'],
    [
        ['首页（仪表板）', 'app.py', '项目概述、数据状态卡片、6 页快速导航、AI 助手配置'],
        ['01 — 数据采集', 'pages/01_数据采集.py', '爬虫配置 + 多源勾选 + 一键执行 + 实时日志'],
        ['02 — 数据管理', 'pages/02_数据管理.py', '文件上传、数据预览、列名映射、质控报告查看'],
        ['03 — 数据可视化', 'pages/03_数据可视化.py', '10 种图表，支持时间范围和行政区筛选'],
        ['04 — 建模训练', 'pages/04_建模训练.py', '特征选择、自适应训练、实时对比、最优模型高亮'],
        ['05 — 模型评测', 'pages/05_模型评测.py', '全指标展示、残差诊断、SHAP 解释、过拟合警告'],
        ['06 — 报告生成', 'pages/06_报告生成.py', '一键生成 7 章报告、HTML/Markdown/ZIP 下载'],
    ]
)

doc.add_heading('9.3 10 种可视化图表', level=2)
add_table(doc,
    ['#', '图表类型', '工具', '用途'],
    [
        ['1', '气象变量时序折线图', 'Pyecharts Line', '查看温度/湿度/风速逐日变化趋势'],
        ['2', '疾病趋势图', 'Pyecharts Bar + Line', '传染病发病数月际变化'],
        ['3', 'Spearman 相关热力图', 'Pyecharts HeatMap', '气象-疾病关联强度矩阵'],
        ['4', '北京区划风险等级地图', 'Pyecharts Map(北京)', '空间分布一目了然'],
        ['5', '温-湿-风 3D 散点图', 'Plotly 3D Scatter', '三维交互探索气象变量关系'],
        ['6', '疾病季节性热力图', 'Pyecharts HeatMap', '月×区 疾病分布模式'],
        ['7', 'SHAP 特征重要性', 'SHAP + Plotly', '模型解释 — 各特征贡献度排序'],
        ['8', '残差诊断四联图', 'Matplotlib', 'QQ/分布/Learning Curve/预测vs真实'],
        ['9', '模型对比雷达图', 'Plotly Radar', '多模型多维指标直观比较'],
        ['10', '模型排名条形图', 'Pyecharts Bar', 'R² 综合得分排序'],
    ]
)

doc.add_heading('9.4 AI 助手', level=2)
doc.add_paragraph(
    '平台内置 AI 助手功能（pages/07_AI助手.py），基于 LLM 对话接口。'
    '支持多服务商（DeepSeek、OpenAI、Ollama 等），API 密钥仅存储在浏览器会话内存中，'
    '关闭后自动清除，永不被写入磁盘，确保安全性。'
    '用户可通过 AI 助手咨询平台使用方法、数据分析解读和模型结果解释。'
)

doc.add_page_break()

# ============================================================
# 十、数据接口契约
# ============================================================
doc.add_heading('十、数据接口契约', level=1)

doc.add_heading('10.1 标准化气象数据 Schema', level=2)
doc.add_paragraph(
    '所有气象数据采集器输出统一为 weather_standard.csv，包含 12 列标准字段：'
)
add_table(doc,
    ['列名', '类型', '说明', '示例'],
    [
        ['station_id', 'str', '区站号（5位）', '54511'],
        ['district', 'str', '行政区（中文）', '海淀'],
        ['date', 'str', '日期 YYYY-MM-DD', '2026-07-10'],
        ['temp_avg', 'float', '日均温 ℃', '27.5'],
        ['temp_max', 'float', '日最高温 ℃', '33.2'],
        ['temp_min', 'float', '日最低温 ℃', '22.1'],
        ['humidity_avg', 'float', '日均相对湿度 %', '65.0'],
        ['precipitation', 'float', '日降水量 mm', '2.5'],
        ['wind_speed_avg', 'float', '日均风速 m/s', '3.2'],
        ['pressure_avg', 'float', '日均气压 hPa', '1005.3'],
        ['source_trust', 'int', '信任度 -1~5', '5'],
        ['provenance_id', 'str', '溯源标识', 'CMA_SURF_20260710_54511'],
    ]
)

doc.add_heading('10.2 标准化疾病数据 Schema', level=2)
doc.add_paragraph(
    '所有疾病数据采集器输出统一为 disease_standard.csv，包含 8 列标准字段：'
)
add_table(doc,
    ['列名', '类型', '说明'],
    [
        ['district', 'str', '行政区（中文）'],
        ['year', 'int', '年份'],
        ['month', 'int', '月份'],
        ['disease_type', 'str', '疾病类型（法定传染病总计/流感/手足口病等）'],
        ['incidence', 'float', '发病率（/10万）'],
        ['cases', 'int', '发病数'],
        ['source_trust', 'int', '信任度 -1~5'],
        ['provenance_id', 'str', '溯源标识'],
    ]
)

doc.add_heading('10.3 信任度体系', level=2)
doc.add_paragraph(
    '每条数据记录都标注了信任度等级，用于下游建模时的质量评估和数据源加权：'
)
add_table(doc,
    ['信任度', '来源', '说明'],
    [
        ['5', 'CMA 官方实测', '国家气象信息中心原始观测数据，最高权威性'],
        ['4', '国际数据库', 'NOAA GSOD/ISD、WHO 数据等'],
        ['3', '政府公开报告', '卫健委/CDC 公报、天气网实况观测'],
        ['2', '第三方实况', '天气网历史均值、天气后报网数据'],
        ['1', '文献提取', '论文附表/补充材料'],
        ['0', '未知来源', '临时数据，未经核实'],
        ['-1', '预报数据', '不入建模训练，仅作趋势参考'],
    ]
)

doc.add_heading('10.4 溯源系统', level=2)
doc.add_paragraph(
    'provenance.py 实现了完整的数据溯源追踪机制。'
    '每条数据记录通过 provenance_id 字段可追溯到：'
)
items = [
    '来源 URL 或文件路径',
    '数据获取时间（精确到秒）',
    '信任度等级',
    '数据类型（观测/预报/历史均值）',
    '采集器版本和执行参数',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')
doc.add_paragraph(
    '溯源记录以 JSON 格式持久化到 logs/provenance.json，'
    '并在报告生成时自动汇总统计（总记录数、可用建模数、各来源占比等）。'
)

doc.add_page_break()

# ============================================================
# 十一、配置与运行指南
# ============================================================
doc.add_heading('十一、配置与运行指南', level=1)

doc.add_heading('11.1 配置文件 (agent/config.yaml)', level=2)
doc.add_paragraph(
    '所有管道参数集中在 agent/config.yaml 中管理，主要包括：'
)
add_table(doc,
    ['配置节', '参数', '说明'],
    [
        ['pipeline.data.sources', '数据源列表', '启用的数据源（CMA_SURF_OBS, WEATHER_COM, BJ_HEALTH_COMM 等）'],
        ['pipeline.data.target_districts', '目标行政区', '北京 18 个区的中文名称列表'],
        ['pipeline.data.disease_type', '疾病类型', '建模目标的疾病种类'],
        ['pipeline.data.time_start/end', '时间范围', '数据采集的时间窗口'],
        ['pipeline.data.clean_rules', '清洗规则', 'missing_strategy, outlier_method, unit_normalization'],
        ['pipeline.model', '模型参数', 'target, test_size, cv_folds, metric, auto_feature_selection'],
        ['pipeline.output', '输出格式', 'formats, auto_report'],
    ]
)

doc.add_heading('11.2 环境依赖', level=2)
add_table(doc,
    ['组件', '最低版本', '用途'],
    [
        ['Python', '3.10+', '运行环境'],
        ['streamlit', '—', 'Web UI 框架'],
        ['pandas, numpy', '—', '数据处理核心'],
        ['scikit-learn', '—', '机器学习基础库'],
        ['xgboost, lightgbm', '—', '梯度提升模型（可选）'],
        ['pyecharts, plotly, matplotlib', '—', '可视化三件套'],
        ['jinja2, pyyaml', '—', '报告模板 + 配置解析'],
        ['shap', '—', '模型可解释性（可选但推荐）'],
        ['pycaret', '—', 'AutoML 增强（可选，不可用时自动降级）'],
    ]
)

doc.add_heading('11.3 核心命令', level=2)
doc.add_paragraph('启动 Web 平台：')
add_code_block(doc, 'streamlit run app.py                    # 浏览器访问 http://localhost:8501')

doc.add_paragraph('全平台验证：')
add_code_block(doc, 'python scripts/verify_all.py             # 5 大类自动核验，期望：✅ 全部通过')

doc.add_paragraph('单独运行数据采集器：')
add_code_block(doc, '''python agent/crawlers/cma_portal.py        # CMA 门户检测 + 注册指南
python agent/crawlers/china_cdc.py         # 中国 CDC / 国家卫健委
python agent/crawlers/beijing_health_data.py  # 北京疾病综合数据
python agent/crawlers/tianqihoubao.py      # 天气后报网历史实况
python agent/crawlers/weather_history.py   # 天气网 40 天 API
python agent/crawlers/bj_health_commission.py  # 北京市卫健委
python agent/crawlers/literature_extract.py  # PDF/Excel 文献提取''')

doc.add_paragraph('Phase 1 数据清洗（独立脚本）：')
add_code_block(doc, '''cd data_scripts/
python clean_surface_weather.py            # 地面观测 TAB → 中文 CSV
python clean_upper_air.py                  # 高空探空 TAB + 气压层映射
python add_city_column.py                  # 站号 → 城市名称
python make_excel_ready.py                 # Excel 兼容处理''')

doc.add_page_break()

# ============================================================
# 十二、质量保证体系
# ============================================================
doc.add_heading('十二、质量保证体系', level=1)

doc.add_heading('12.1 自动核验脚本', level=2)
doc.add_paragraph(
    'scripts/verify_all.py 是平台的全自动质量核验工具，'
    '运行后执行 5 大类检查，确保数据准确性和系统完整性：'
)
add_table(doc,
    ['#', '核验类别', '检查内容', '阈值/标准'],
    [
        ['1', '气象数据完整性', '行数=126, 列数=12, 18站, 18区', '精确匹配'],
        ['2', '气象-原始交叉验证', '逐行比对 CMA 原始日均温，计算温差', '温差 ≤ 0.01°C'],
        ['3', '物理范围校验', '温度/湿度/气压是否在物理合理范围内', '不得有违规值'],
        ['4', '高空温度递减', '地面温度 > 高层温度', '物理规律必须满足'],
        ['5', '疾病季节性', '冬季(11-2月)均值 > 夏季(6-8月)均值', '呼吸道疾病模式'],
        ['6', '溯源覆盖度', '溯源记录总数', '> 1000 条'],
        ['7', '文件完整性', '30 个必要文件逐一检查', '不得缺失'],
    ]
)

doc.add_heading('12.2 数据真实性保障', level=2)
doc.add_paragraph('平台采取以下措施确保数据真实性：')
items = [
    '所有数据记录通过 provenance_id 字段可追溯到源文件/URL',
    '质控报告列出每个数据源的信任度等级',
    '报告中无"模拟数据""合成数据"字样',
    '缺失字段标注"数据不可用"而非填充假值',
    '天气预报数据标记 source_trust = -1，不进入建模训练',
    '原始 TXT 文件不可移动或删除，脚本依赖固定路径复现',
]
for item in items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('12.3 已知限制与缓解措施', level=2)
add_table(doc,
    ['#', '限制', '影响', '缓解措施'],
    [
        ['1', 'CMA 地面数据仅 7 天', '训练样本不足，模型仅供参考', '注册 CMA 获取更长时序；使用天气后报网扩展'],
        ['2', '疾病数据为市级总量', '无分区分病种数据，无法空间精细化', '标注限制，留出数据上传接口'],
        ['3', '天气网数据为预报值', '无法作为建模输入', '已标记 trust=-1，仅作参考'],
        ['4', 'CMA 门户需注册', '新用户无法直接 API 获取', '已生成注册指南 raw/CMA_数据获取指南.md'],
        ['5', 'CDC/卫健委有反爬', '自动采集不稳定', '已生成替代方案指南 raw/CDC_数据获取指南.md'],
    ]
)

doc.add_heading('12.4 Harness 工程体系', level=2)
doc.add_paragraph(
    '项目集成了 Harness AI 协作工程体系（L2 成熟度），提供以下自动化能力：'
)
add_table(doc,
    ['组件', '类型', '功能'],
    [
        ['SessionStart Hook', '自动注入', '会话开始时注入 git 状态、项目进度、最近审查记录'],
        ['PreToolUse Hook', '安全拦截', '拦截 .env 写入、危险 shell 命令等不安全的工具调用'],
        ['Stop Hook', '自动审查', '每次响应结束后生成审查报告至 .claude/reviews/（按日期累积）'],
        ['harness-gc Skill', '自治扫描', '8 维项目健康检查'],
        ['harness-start Skill', '四步初始化', '初始化 → 看架构 → 删多余 → 目录体检'],
        ['tech-review Skill', '技术审查', '技术方案最佳实践审查'],
        ['verify-goal Skill', '目标验证', '多步骤任务完成后验收'],
    ]
)

doc.add_page_break()

# ============================================================
# 附录
# ============================================================
doc.add_heading('附录', level=1)

doc.add_heading('A. 项目文件结构', level=2)
doc.add_paragraph('完整的项目目录树（核心文件）：')
file_tree = '''项目根目录/
├── app.py                          # Streamlit 主入口（首页仪表板）
├── pages/                          # 6 个 Web 功能页面
│   ├── 01_数据采集.py              # 爬虫配置 + 执行 + 实时日志
│   ├── 02_数据管理.py              # 数据上传 + 清洗预览 + 质控报告
│   ├── 03_数据可视化.py            # 10 种图表（地图/趋势/关联/诊断）
│   ├── 04_建模训练.py              # 特征选择 + 模型对比 + 训练监控
│   ├── 05_模型评测.py              # 全指标 + 残差诊断 + SHAP + 排序
│   ├── 06_报告生成.py              # 一键生成报告 + ZIP/HTML 下载
│   └── 07_AI助手.py               # LLM 对话助手
│
├── agent/                          # 智能体核心
│   ├── pipeline.py                 # AgentPipeline 调度引擎
│   ├── config.py + config.yaml     # 配置系统
│   ├── provenance.py               # 数据溯源追踪
│   ├── features.py                 # 特征工程
│   ├── visualizer.py               # 10 种图表工厂
│   ├── llm_assistant.py            # LLM 助手接口
│   ├── agents/                     # 5 个智能体
│   │   ├── crawl_agent.py          # 多源数据采集调度器
│   │   ├── clean_agent.py          # 自适应清洗 + 质控报告
│   │   ├── model_agent.py          # AutoML 自适应建模
│   │   ├── eval_agent.py           # 多维评测 + SHAP 解释
│   │   └── report_agent.py         # Jinja2 报告生成
│   └── crawlers/                   # 7 个独立数据源爬虫
│       ├── weather_history.py      # 中国天气网 40 天 API
│       ├── tianqihoubao.py         # 天气后报网历史实况
│       ├── cma_portal.py           # CMA 国家气象科学数据中心
│       ├── bj_health_commission.py # 北京市卫健委疫情公告
│       ├── beijing_health_data.py  # 北京市疾病数据综合采集器
│       ├── china_cdc.py            # 中国 CDC / 国家卫健委
│       └── literature_extract.py   # PDF/Excel 文献数据提取
│
├── data_scripts/                   # Phase 1 数据清洗工具
│   ├── clean_surface_weather.py    # 地面气象 TAB 清洗
│   ├── clean_upper_air.py          # 高空探空 TAB 清洗 + 气压层映射
│   ├── add_city_column.py          # 区站号 → 城市名称
│   ├── make_excel_ready.py         # Excel/WPS 兼容 CSV
│   └── fix_csv_encoding.py         # 通用编码修复
│
├── crawler/                        # Phase 1 天气网爬虫
│   └── crawl_weather_history.py    # 天气网 40 天日历爬虫
│
├── output/                         # 标准化数据产出
│   ├── weather_standard.csv        # 气象数据标准格式（126行×12列）
│   ├── upper_air_standard.csv      # 高空数据标准格式（249行×14列）
│   ├── disease_standard.csv        # 疾病数据标准格式（98行×8列）
│   ├── 数据质控报告.md              # 6 章质控分析
│   └── 字段释义文档.md              # 所有字段详细说明
│
├── models/                         # 训练好的模型文件
│   ├── best_model.pkl              # sklearn 兼容模型对象
│   ├── model_ranking.json          # 模型排名 + 全部指标
│   └── feature_config.json         # 特征配置
│
├── reports/                        # 生成的报告（按时间戳归档）
├── logs/                           # 结构化 JSON 日志 + 溯源记录
├── raw/                            # 原始采集数据 + 数据获取指南
├── templates/report.md.j2          # Jinja2 报告模板
├── scripts/verify_all.py           # 全平台数据核验脚本
└── CLAUDE.md                       # 项目 AI 协作规则
'''
add_code_block(doc, file_tree)

doc.add_heading('B. 产出文件速查', level=2)
add_table(doc,
    ['目录', '用途', '关键文件'],
    [
        ['output/', '标准化数据集', 'weather_standard.csv, disease_standard.csv, 数据质控报告.md'],
        ['raw/', '原始采集数据', 'beijing_disease_monthly.csv, CMA_数据获取指南.md, CDC_数据获取指南.md'],
        ['models/', '训练产物', 'best_model.pkl, model_ranking.json, feature_config.json'],
        ['logs/', '运行日志 + 溯源', 'provenance.json, crawl_*.log, clean_*.log, pipeline_*.json'],
        ['reports/', '生成的报告', '按时间戳归档的 HTML + MD + ZIP'],
    ]
)

doc.add_heading('C. 快速命令速查', level=2)
add_code_block(doc, '''# === 启动平台 ===
streamlit run app.py

# === 全平台验证 ===
python scripts/verify_all.py

# === 数据采集（7 个爬虫） ===
python agent/crawlers/cma_portal.py              # CMA 门户检测 + 注册指南
python agent/crawlers/china_cdc.py               # 中国 CDC / 国家卫健委
python agent/crawlers/beijing_health_data.py     # 北京疾病综合数据
python agent/crawlers/tianqihoubao.py            # 天气后报网
python agent/crawlers/weather_history.py         # 天气网 40 天 API
python agent/crawlers/bj_health_commission.py    # 北京市卫健委
python agent/crawlers/literature_extract.py      # 文献提取

# === Phase 1 数据清洗 ===
cd data_scripts/
python clean_surface_weather.py                  # 地面气象数据清洗
python clean_upper_air.py                        # 高空气象数据清洗
python make_excel_ready.py <文件路径>            # Excel 兼容处理

# === Harness 工程 ===
node scripts/check.mjs                           # 健康检查
node scripts/gc-scan.mjs                         # GC 自治扫描''')

# ============================================================
# 保存文档
# ============================================================
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'output', '项目详细说明文档.docx')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
doc.save(output_path)

file_size_kb = os.path.getsize(output_path) / 1024
print(f'✅ 文档生成成功！')
print(f'   路径：{output_path}')
print(f'   大小：{file_size_kb:.1f} KB')
