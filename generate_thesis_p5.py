"""
论文正文生成器 Part 5 — 第4章 系统实现与关键技术
"""
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

INPUT_PATH = "北京市气候健康风险预警—智能体可视化平台_毕业论文.docx"
doc = Document(INPUT_PATH)

def add_para(text, bold=False, alignment=None, font_name='宋体', font_size=Pt(12),
             first_line_indent=Cm(0.74), space_before=0, space_after=0):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = Pt(20)
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
    if level == 1:
        doc.add_page_break()
    return doc.add_heading(text, level=level)

# ============================================================
# 第4章 系统实现与关键技术
# ============================================================
add_heading("4  系统实现与关键技术", level=1)

add_para(
    "本章详细阐述各功能模块的具体实现方法、核心代码逻辑和技术细节。系统后端由约8,000行"
    "Python代码构成，前端基于Streamlit框架实现约2,200行Web交互代码，配置文件约36行YAML。"
    "以下按模块逐一介绍实现细节。"
)

add_heading("4.1  多源气象数据采集实现", level=2)

add_heading("4.1.1  地面气象数据采集", level=3)
add_para(
    "地面气象观测数据来源于国家气象信息中心发布的TAB分隔文本文件。数据覆盖北京市18个气象"
    "观测台站，时间范围覆盖2026年7月5日至7月11日（7天），每日包含0时、3时、6时、9时、"
    "12时、15时、18时和21时共8个观测时次。原始文件通过data_scripts/clean_surface_weather.py"
    "进行处理，该脚本的核心实现流程为：（1）使用pandas的read_csv函数读取TAB分隔文件，"
    "指定编码为UTF-8；（2）根据字段位置进行列切分，提取区站号、年月日时次、气压、气温、"
    "相对湿度、风向风速、降水量等要素；（3）使用哨兵值映射表将特殊值（999017、999990等）"
    "转换为NaN；（4）通过区站号-行政区名称映射字典（18个台站对应15个行政区）自动填充"
    "城市名称列；（5）输出为包含22个字段的标准CSV文件。"
)
add_para(
    "处理后的地面气象标准数据集（surface_weather_clean_excel_ready.csv）包含882行记录"
    "和22列字段，字段涵盖：区站号、城市名称、年、月、日、时次、气压、海平面气压、最高"
    "气压、最低气压、最大风速、极大风速、极大风速的风向、2分钟平均风向、2分钟平均风速、"
    "最大风速的风向、温度/气温、最高气温、最低气温、相对湿度、最小相对湿度、过去3小时降水量。"
    "数据完整率达到98.5%以上，主要的缺失出现在风向相关字段（部分时次无风向记录）。"
)

add_heading("4.1.2  高空气象数据采集", level=3)
add_para(
    "高空气象观测数据同样来源于国家气象信息中心。高空探空数据通过无线电探空仪获取，每日"
    "仅00:00和12:00 UTC两个时次（对应北京时08:00和20:00），包含从地面到约30km高空的"
    "多层气压层探测数据。处理脚本data_scripts/clean_upper_air.py的工作流程包括："
    "（1）读取TAB分隔原始文件；（2）根据垂直探测意义（EVSS字段）区分地面层数据（EVSS="
    "131072，即2^17）和标准气压层数据（EVSS=65536，即2^16）；（3）将标准气压层数值"
    "（1000、925、850、700、500、400、300、250、200、150、100、70、50、30、20、10、"
    "7、5、3、2、1 hPa）映射为可读的标签；（4）提取气压、位势高度、风向、风速、温度、"
    "露点温度、温度露点差等要素。处理后的数据集包含249行记录和19列字段。"
)

add_heading("4.1.3  天气网站数据爬取", level=3)
add_para(
    "中国天气网（weather.com.cn）数据爬虫通过分析其日历API和HTML页面的数据结构实现。"
    "crawler/crawl_weather_history.py脚本实现了三种数据类型的采集：（1）历史均值数据"
    "——通过calendar_new API接口获取指定日期范围的多年历史平均气温和降水量；（2）实况"
    "数据（obs）——通过解析实况天气HTML页面，提取当日的实际最高/最低气温和降水量；"
    "（3）预报数据（d15/d40）——通过解析7天/15天/40天预报HTML页面，获取未来的预报"
    "气温和降水概率。三种数据按照优先级排序（实况 > 预报 > 历史均值），当同一个日期存在"
    "多个来源的数据时，保留优先级最高的数据。最终输出为124行×7列的标准化数据集，时间"
    "跨度约3个月（2026年4月26日至8月1日）。"
)

add_heading("4.1.4  疾病数据采集", level=3)
add_para(
    "疾病数据采集模块包含三个爬虫：北京市卫健委爬虫（bj_health_commission.py）用于获取"
    "北京地区法定传染病疫情月报数据，通过解析北京市卫健委官网发布的疫情通告HTML页面提取"
    "发病人数、发病率等统计数据；中国CDC爬虫（china_cdc.py）用于获取全国层面的传染病监测"
    "数据作为对照参考；北京健康数据综合采集器（beijing_health_data.py）是一个聚合爬虫，"
    "整合多个来源的北京地区疾病统计信息。由于疾病数据具有较强的时效性和发布周期（通常按月"
    "更新），系统设计了定时增量采集机制和本地缓存策略，确保数据的及时性和完整性。"
)

add_heading("4.1.5  Excel兼容性处理", level=3)
add_para(
    "为满足实际业务场景中使用Microsoft Excel和WPS打开数据文件的需求，系统实现了专门的"
    "Excel兼容性处理脚本（data_scripts/make_excel_ready.py）。该脚本执行以下处理："
    "（1）在文件头部添加UTF-8 BOM标记（\\xef\\xbb\\xbf），确保Excel正确识别中文编码；"
    "（2）将行尾符从LF转换为CRLF（Windows标准）；（3）对日期列使用Excel保护公式"
    "（=\\\"YYYY-MM-DD\\\"），防止Excel自动将日期转换为其他格式；（4）对以零开头的区站号"
    "列使用保护公式（=\\\"区站号\\\"），防止Excel自动去掉前导零。"
)

add_heading("4.2  自适应数据清洗与质控实现", level=2)
add_para(
    "CleanAgent（agent/agents/clean_agent.py）实现了五阶段自适应数据清洗管线。其核心"
    "实现逻辑如下："
)
add_para(
    "第一阶段——格式标准化：通过CN_TO_EN_COLUMN_MAP字典（定义在features.py中）将中文"
    "列名映射为英文标准名，如“温度/气温”→\"temp_avg\"、“相对湿度”→\"humidity_avg\"等。"
    "日期字段使用pd.to_datetime统一解析为datetime类型，再格式化为\"YYYY-MM-DD\"字符串。"
    "数值列使用pd.to_numeric(errors='coerce')强制转换为浮点数，无法转换的值自动变为NaN。"
)
add_para(
    "第二阶段——哨兵值处理：维护SENTINEL_MAP字典，定义哨兵值到目标值的映射规则。"
    "例如：{999017: np.nan}表示将风向哨兵值转换为缺失值；{999990: np.nan}表示将降水量"
    "哨兵值转换为缺失值。对于气压领域的999.x系列值，由于这些值可能包含有效的物理信息"
    "（如气压订正值），根据哨兵值的物理含义选择保留原值或转换为NaN。处理过程记录在案，"
    "输出哨兵值处理统计报告。"
)
add_para(
    "第三阶段——缺失值诊断与修复：对每个数值列调用isnull().sum()计算缺失值计数和"
    "缺失率。根据缺失率选择处理策略：若缺失率<5%，使用interpolate(method='linear')"
    "进行时间序列线性插值；若缺失率在5%-20%之间，使用fillna方法以同一行政区其他台站的"
    "中位数值填补；若缺失率>20%，保留NaN并在质控报告中标记为不可靠。对于系统性缺失"
    "（如某台站长期缺测某要素），额外输出警告建议。"
)
add_para(
    "第四阶段——异常值检测：对每个数值列计算Q1（25%分位数）、Q3（75%分位数）和IQR"
    "（Q3-Q1），定义正常值范围为[Q1-1.5×IQR, Q3+1.5×IQR]。超出此范围的值被标记"
    "但保留原值，同时输出异常值列表供用户审核。此外，结合气象学物理阈值进行二次校验，"
    "如北京地区夏季气温合理范围为[-20°C, 50°C]，超出物理范围的值直接报告为错误数据。"
)
add_para(
    "第五阶段——质控报告生成：使用Python字符串模板生成Markdown格式的质控报告"
    "（数据质控报告.md），内容包括：各字段的完整率统计表、哨兵值处理记录、缺失值修复"
    "方法及修复量、异常值检测结果、单位转换记录。同时生成字段释义文档（字段释义文档.md），"
    "对每个输出字段的定义、单位、取值范围和注意事项进行详细说明。"
)

add_heading("4.3  特征工程与数据预处理实现", level=2)
add_para(
    "FeatureEngineer（agent/features.py）实现了完整的特征工程流水线，将原始气象时序数据"
    "转化为可用于机器学习建模的特征矩阵。"
)

add_heading("4.3.1  日粒度聚合", level=3)
add_para(
    "地面气象数据原始粒度为3小时间隔（每日8个时次），在建模前需要聚合为日粒度。聚合策略"
    "根据变量性质分类处理：对于气温、气压、湿度等连续变量，使用groupby(['station_id', "
    "'date']).mean()计算日均值；对于最高/最低气温，使用max()/min()提取日极值；对于降水量，"
    "使用sum()计算日累计量；对于风向，使用mode()提取日主导风向。聚合后每日每个台站产生"
    "一条日值记录，大大降低了数据维度（从8条/天降至1条/天），同时保留了完整的气象日变化"
    "信息。"
)

add_heading("4.3.2  滞后特征构造", level=3)
add_para(
    "滞后特征（Lag Features）通过pandas的shift()方法实现。对于目标疾病变量和关键气象要素"
    "（气温、湿度、降水量），分别构造shift(1)、shift(2)、shift(3)三个滞后期的特征列。"
    "例如，humidity_avg_lag1表示前一天的湿度值，humidity_avg_lag2表示前两天的湿度值。"
    "滞后特征的引入基于气象-健康的流行病学滞后效应假设：气象条件的变化往往在1-3天后才对"
    "人体健康产生可观测的影响。对于因滞后产生的前导NaN值（前3天无历史数据），使用该序列"
    "的全局中位数进行填充。"
)

add_heading("4.3.3  滑动窗口特征构造", level=3)
add_para(
    "滑动窗口特征（Rolling Features）通过pandas的rolling(window=3)方法实现，捕捉短期"
    "气象变化趋势。对温度变量构造rolling(3).mean()（3天滑动均值）和rolling(3).std()"
    "（3天滑动标准差），前者反映近3天的平均温度水平，后者反映温度波动幅度（波动越大，"
    "对人体适应能力的挑战越大）。对降水量构造rolling(3).sum()（3天累计降水量），反映"
    "近期的降水累积效应。对湿度变量构造rolling(3).mean()（3天滑动平均湿度）。滑动窗口"
    "宽度设为3天，与滞后特征的最大滞后期保持一致。"
)

add_heading("4.3.4  极端天气标记与时间特征", level=3)
add_para(
    "极端天气标记使用pandas的布尔索引生成二值（0/1）特征列。高温标记extreme_heat通过"
    "df['temp_max'] >= 35生成，其中35°C为中国气象学定义的高温日阈值；暴雨标记heavy_rain"
    "通过df['precipitation'] >= 50生成，50mm/24h为暴雨的最低等级标准；大风标记"
    "strong_wind通过df['wind_speed_max'] >= 10.8生成，10.8m/s为蒲福风级六级（强风）"
    "的阈值。时间特征使用pd.get_dummies(df['month'], prefix='month')生成12列月份哑变量，"
    "每个月份一个二值列，drop_first=False保留所有12列以保持完整性。"
)

add_heading("4.3.5  特征筛选与数据划分", level=3)
add_para(
    "特征筛选使用sklearn.feature_selection.RFE（递归特征消除），以LightGBM为基学习器，"
    "设置n_features_to_select为总特征数的70%（向上取整），逐步消除最不重要的特征。RFE通过"
    "coef_或feature_importances_属性对特征进行排序，在每轮迭代中移除权重最低的特征，直到"
    "达到目标特征数量。数据划分使用时间序列分层划分——按日期排序后取前80%为训练集、后20%"
    "为测试集，严格禁止随机打乱索引，以保证时间先后顺序不被破坏，防止未来信息泄漏。"
    "训练集（train_split.csv）和测试集（test_split.csv）分别持久化至models/目录。"
)

add_heading("4.4  多模型自适应建模实现", level=2)
add_para(
    "ModelAgent（agent/agents/model_agent.py）是多模型自适应建模的核心实现模块，约530行"
    "代码。其核心类ModelTrainer封装了模型训练、交叉验证、超参数优化和模型对比的完整逻辑。"
)

add_heading("4.4.1  模型池构建", level=3)
add_para(
    "模型池定义为一个Python字典列表model_pool，每项包含模型名称、sklearn兼容的estimator"
    "实例、以及超参数搜索网格param_grid。池中的10个模型及其超参数网格如下："
)
add_para(
    "（1）LightGBM：学习率[0.01, 0.05, 0.1]，树数量[100, 200, 300]，最大深度[3, 5, 7, -1]；"
    "（2）XGBoost：学习率[0.01, 0.05, 0.1]，树数量[100, 200]，最大深度[3, 5, 7]；"
    "（3）随机森林：树数量[100, 200, 300]，最大深度[5, 10, 15, None]；"
    "（4）Extra Trees：树数量[100, 200]，最大深度[5, 10, None]；"
    "（5）KNN：邻居数[3, 5, 7, 9]，权重策略['uniform', 'distance']；"
    "（6）SVR：正则化C[0.1, 1, 10]，核函数['linear', 'rbf']，gamma['scale', 'auto']；"
    "（7）线性回归：无超参数（使用默认配置作为基线）；"
    "（8）Ridge：正则化alpha[0.01, 0.1, 1, 10, 100]；"
    "（9）Lasso：正则化alpha[0.0001, 0.001, 0.01, 0.1, 1]；"
    "（10）ElasticNet：正则化alpha[0.001, 0.01, 0.1]，L1比例l1_ratio[0.1, 0.5, 0.9]。"
)

add_heading("4.4.2  训练与优化流程", level=3)
add_para(
    "对模型池中的每个模型，执行以下训练与优化流程：首先，使用sklearn的TimeSeriesSplit"
    "（n_splits=5）创建时间序列交叉验证划分器，确保每折的训练数据时间早于验证数据。"
    "然后，使用GridSearchCV执行网格搜索，cv参数设置为TimeSeriesSplit实例，scoring参数"
    "设置为'r2'，n_jobs=-1以利用全部CPU核心并行加速。GridSearchCV对param_grid中的所有"
    "参数组合进行穷举搜索，返回交叉验证R²均值最高的最佳参数组合。"
)
add_para(
    "最佳模型确定后，在完整训练集上以最佳参数重新训练，然后在测试集上进行预测。计算并记录"
    "全部7项评估指标（R²、调整R²、MAE、MSE、RMSE、MAPE、Max Error、CV-R²均值和标准差）。"
    "模型的运行得分按综合评分公式计算：score = 0.4×R² + 0.3×CV-R²均值 + 0.2×(1-MAPE)"
    " + 0.1×exp(-RMSE/100)。该公式综合权衡了拟合优度（R²）、泛化能力（CV-R²）、相对误差"
    "（MAPE）和绝对误差（RMSE）四个维度，权重分配经过多次实验验证，确保评分结果与人工"
    "专家判断高度一致。"
)

add_heading("4.4.3  模型持久化", level=3)
add_para(
    "训练完成后，最优模型及其元数据通过以下方式持久化：最佳模型使用joblib.dump()序列化为"
    "best_model.pkl文件（约135KB）；特征配置（特征列名列表、RFE筛选结果）保存为feature_"
    "config.json；模型排名和全部评估指标保存为model_ranking.json；训练集和测试集以CSV格式"
    "保存供后续审计。所有文件存储于models/目录，支持模型的快速加载和复用。"
)

add_heading("4.5  全维度模型评测实现", level=2)
add_para(
    "EvalAgent（agent/agents/eval_agent.py）实现了全维度的模型评测与智能诊断功能。评测"
    "流程如下："
)
add_para(
    "步骤一：指标计算。对入选模型使用sklearn.metrics模块中的r2_score、mean_absolute_error、"
    "mean_squared_error、mean_absolute_percentage_error和max_error函数分别计算R²、MAE、"
    "MSE、MAPE和Max Error；RMSE由MSE开方得到；调整R²由公式R²_adj = 1 - (1-R²)(n-1)"
    "/(n-p-1)手动计算，其中n为测试样本数，p为特征数；CV指标的均值和标准差从GridSearchCV"
    "的cv_results_字典中提取。"
)
add_para(
    "步骤二：过拟合/欠拟合检测。对比训练集R²（从GridSearchCV的best_score_获取）与测试集"
    "R²：若训练R² - 测试R² > 0.05，判定为过拟合；若训练R² < 0.6且测试R² < 0.6，判定为"
    "欠拟合；其余情况判定为拟合良好。检测结果记录在evaluation字段中。"
)
add_para(
    "步骤三：残差诊断。计算残差序列residuals = y_test - y_pred，绘制：（1）残差vs拟合值"
    "散点图——用于检验方差齐性（homoscedasticity），理想的残差图应随机散布在零线两侧，"
    "不呈现漏斗形或曲线形模式；（2）残差Q-Q图（Quantile-Quantile Plot）——使用scipy."
    "stats.probplot将残差分位数与标准正态分布的理论分位数对比，若点阵基本沿对角线分布，"
    "则残差近似正态，表明模型假设得到满足。"
)
add_para(
    "步骤四：SHAP可解释性分析。使用SHAP（SHapley Additive exPlanations）库计算每个特征"
    "对模型预测的边际贡献。具体使用shap.TreeExplainer（适用于树模型）或shap.KernelExplainer"
    "（适用于非树模型）计算SHAP值，生成：（1）SHAP特征重要性条形图——按特征平均绝对SHAP值"
    "降序排列，直观展示各特征对预测的总体贡献；（2）SHAP汇总蜂群图——以散点形式展示每个"
    "样本每个特征的SHAP值分布，颜色编码特征值的高低（红色为高值、蓝色为低值），揭示特征"
    "值大小与预测方向的关系。"
)

add_heading("4.6  智能体全流程自动化实现", level=2)
add_para(
    "AgentPipeline（agent/pipeline.py，约689行）是平台自动化能力的核心引擎。它读取YAML"
    "配置文件（agent/config.yaml），按照预设的六步顺序依次调度六个专用智能体，实现从数据"
    "采集到报告生成的全流程无人自动化。"
)

add_heading("4.6.1  Pipeline调度机制", level=3)
add_para(
    "AgentPipeline的run()方法是流程调度的入口。它依次调用_run_step方法执行六个步骤，每步"
    "接收一个step_fn回调函数（封装了对应智能体的业务逻辑）和一个progress_callback可选回调"
    "（用于向Web前端推送进度更新）。每个步骤的执行被包装在try-except块中，确保单步失败"
    "不会导致整个管线崩溃——失败的步骤被标记为failed状态并记录错误堆栈，后续步骤可选择"
    "跳过或继续执行（取决于错误严重程度）。"
)
add_para(
    "步骤间的数据传递通过self.cache字典实现——前一步的输出数据存入cache，后一步从cache"
    "中读取。例如，Step1（Crawl）将气象CSV路径存入cache['weather_csv']，Step2（Clean）"
    "从cache中读取该路径进行清洗，清洗完毕后将干净DataFrame存入cache['clean_df']，依此类推。"
    "这种松耦合的数据传递方式使得各步骤能够独立开发和测试。"
)

add_heading("4.6.2  异常检测与人工复核机制", level=3)
add_para(
    "每步执行完毕后，AgentPipeline检查返回的anomalies列表。若anomalies非空，当前步骤的"
    "状态被设置为paused（暂停），并在日志中记录异常详情。在Streamlit Web界面中，暂停状态"
    "会触发醒目的警告提示，要求用户介入复核。用户可以选择：（1）忽略异常继续执行——确认"
    "异常不影响后续分析；（2）修正后重试——在解决问题后重新运行当前步骤；（3）终止流程"
    "——放弃当前运行，导出已有结果。这种\"自动执行+异常暂停\"的混合模式在保证效率的同时，"
    "提供了人类专家监督的安全兜底。"
)

add_heading("4.6.3  溯源追踪与日志系统", level=3)
add_para(
    "ProvenanceTracker（agent/provenance.py）实现了完整的数据溯源追踪机制。每次数据采集"
    "操作调用tracker.record()方法记录以下信息：数据来源标识（如CMA_SURF_OBS）、源URL或"
    "文件路径、信任度评分（1-5，5最高）、数据类型（observation/forecast/history）、采集"
    "时间戳、附加说明等。所有溯源记录以追加式JSON日志（JSONL格式）写入logs/目录，每行"
    "为一个JSON对象，便于后续的程序化解析和审计。"
)
add_para(
    "管线运行日志同样采用JSONL格式，以pipeline_{session_id}.json命名，记录每个步骤的开始"
    "时间、结束时间、耗时、状态、异常信息和错误堆栈（如有）。日志系统确保每一次分析运行"
    "都有完整的记录可供回溯，满足科研可重复性和业务可审计性的要求。"
)

add_heading("4.7  AI助手与报告生成实现", level=2)

add_heading("4.7.1  LLM AI助手集成", level=3)
add_para(
    "AI助手模块（agent/llm_assistant.py，约308行）为平台集成了大语言模型驱动的智能问答"
    "功能。模块设计采用Provider抽象模式——定义PROVIDER_PRESETS字典，预置主流LLM服务商的"
    "配置信息（API基础URL、默认模型名称、服务商标签），当前支持的提供商包括DeepSeek、"
    "OpenAI和Ollama（本地部署）。用户在Web侧边栏中选择服务商并输入API密钥后，即可通过"
    "自然语言对话向AI咨询平台使用方法、数据分析解读和模型结果解释。"
)
add_para(
    "安全设计方面：（1）API密钥仅存储在Streamlit的session_state中（浏览器会话内存），"
    "关闭页面后自动清除，从未被写入磁盘或日志文件；（2）每次对话的上下文限制为最近10轮，"
    "防止敏感信息在上下文中的长时间驻留；（3）用户的清除密钥操作会同时清空密钥和所有对话"
    "历史，确保隐私数据的彻底删除。AI助手使用OpenAI兼容的API协议（/chat/completions端点），"
    "因此可兼容所有采用该协议的LLM服务。"
)

add_heading("4.7.2  报告自动生成", level=3)
add_para(
    "ReportAgent（agent/agents/report_agent.py）基于Jinja2模板引擎实现报告的自动生成。"
    "报告模板定义在agent/templates/目录下，采用HTML+CSS样式定义，支持嵌入式交互图表"
    "（通过Plotly的to_html方法）、格式化表格和数学公式渲染。报告生成流程为："
    "（1）从cache中读取各步骤的产出数据；（2）调用Visualizer生成10种图表，导出为HTML"
    "嵌入片段和PNG图片文件；（3）将数据、图表、评测指标和模型结果传入Jinja2渲染上下文；"
    "（4）渲染HTML报告模板，生成完整的分析报告；（5）将所有产物（报告HTML文件、图表PNG"
    "文件、数据CSV文件、模型文件、评测JSON文件）打包为ZIP压缩包供用户下载。报告的7个章节"
    "依次为：数据概览、清洗质控摘要、探索性数据分析、特征工程说明、模型对比结果、最优模型"
    "详解（含SHAP解释）、结论与建议。"
)

doc.save(INPUT_PATH)
print("第4章完成并已保存。")
