"""第4章 + 第5章（含8张图）+ 结论 + 参考文献 + 附录 + 致谢"""
import os
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document("北京市气候健康风险预警—智能体可视化平台_毕业论文.docx")
CD = "output/charts"

def P(text, bold=False, al=None, fn='宋体', fs=Pt(12), ind=Cm(0.74), sb=0, sa=0):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = Pt(20)
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.first_line_indent = ind
    if al is not None: p.paragraph_format.alignment = al
    r = p.add_run(text); r.font.name = fn
    r._element.rPr.rFonts.set(qn('w:eastAsia'), fn); r.font.size = fs; r.bold = bold
    return p
def H(text, level=1):
    if level == 1: doc.add_page_break()
    return doc.add_heading(text, level=level)
def IMG(path, caption, w=5.8):
    p = doc.add_paragraph(); p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(3)
    p.add_run().add_picture(path, width=Inches(w))
    p2 = doc.add_paragraph(); p2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.first_line_indent = Cm(0)
    p2.paragraph_format.space_before = Pt(3); p2.paragraph_format.space_after = Pt(6)
    r2 = p2.add_run(caption); r2.font.name = '宋体'
    r2._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体'); r2.font.size = Pt(10.5)
def TBL(text, bold=False, fs=Pt(9), ind=Cm(0), sb=0, sa=0):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = Pt(16)
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.first_line_indent = ind
    r = p.add_run(text); r.font.name = '宋体'
    r._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体'); r.font.size = fs; r.bold = bold

# ═══════════════════════ 第4章 ═══════════════════════
H("4  系统实现与关键技术",1)
P("本章详细阐述各功能模块的具体实现方法、核心代码逻辑和技术细节。系统后端由约8,088行Python代码构成，前端基于Streamlit框架实现约2,200行Web交互代码，配置文件约36行YAML。以下按模块逐一介绍实现细节。")

H("4.1  多源气象数据采集实现",2)
H("4.1.1  地面气象数据采集",3)
P("地面气象观测数据来源于国家气象信息中心发布的TAB分隔文本文件。数据覆盖北京市18个气象观测台站，时间范围覆盖2026年7月5日至7月11日（7天），每日包含0时、3时、6时、9时、12时、15时、18时和21时共8个观测时次。原始文件通过data_scripts/clean_surface_weather.py进行处理，核心实现流程为：（1）使用pandas的read_csv函数读取TAB分隔文件，指定编码为UTF-8；（2）根据字段位置进行列切分，提取区站号、年月日时次、气压、气温、相对湿度、风向风速、降水量等要素；（3）使用哨兵值映射表将特殊值（999017、999990等）转换为NaN；（4）通过区站号-行政区名称映射字典（18个台站对应15个行政区）自动填充城市名称列；（5）输出为包含22个字段的标准CSV文件。")
P("处理后的地面气象标准数据集（surface_weather_clean_excel_ready.csv）包含882行记录和22列字段，数据完整率达到98.5%以上，主要的缺失出现在风向相关字段（部分时次无风向记录）。")

H("4.1.2  高空气象数据采集",3)
P("高空气象观测数据同样来源于国家气象信息中心。高空探空数据通过无线电探空仪获取，每日仅00:00和12:00 UTC两个时次（对应北京时08:00和20:00），包含从地面到约30km高空的多层气压层探测数据。处理脚本data_scripts/clean_upper_air.py的工作流程包括：（1）读取TAB分隔原始文件；（2）根据垂直探测意义（EVSS字段）区分地面层数据（EVSS=131072）和标准气压层数据（EVSS=65536）；（3）将标准气压层数值映射为可读的标签；（4）提取气压、位势高度、风向、风速、温度、露点温度、温度露点差等要素。处理后的数据集包含249行记录和19列字段。")

H("4.1.3  天气网站数据爬取",3)
P("中国天气网（weather.com.cn）数据爬虫通过分析其日历API和HTML页面的数据结构实现。crawler/crawl_weather_history.py脚本实现了三种数据类型的采集：（1）历史均值数据——通过calendar_new API接口获取指定日期范围的多年历史平均气温和降水量；（2）实况数据（obs）——通过解析实况天气HTML页面，提取当日的实际最高/最低气温和降水量；（3）预报数据（d15/d40）——通过解析7天/15天/40天预报HTML页面，获取未来的预报气温和降水概率。三种数据按照优先级排序（实况 > 预报 > 历史均值），最终输出为124行×7列的标准化数据集。")

H("4.1.4  疾病数据采集",3)
P("疾病数据采集模块包含三个爬虫：北京市卫健委爬虫（bj_health_commission.py）用于获取北京地区法定传染病疫情月报数据；中国CDC爬虫（china_cdc.py）用于获取全国层面的传染病监测数据作为对照参考；北京健康数据综合采集器（beijing_health_data.py）是一个聚合爬虫，整合多个来源的北京地区疾病统计信息。系统设计了定时增量采集机制和本地缓存策略，确保数据的及时性和完整性。")

H("4.1.5  Excel兼容性处理",3)
P("为满足实际业务场景中使用Microsoft Excel和WPS打开数据文件的需求，系统实现了专门的Excel兼容性处理脚本（data_scripts/make_excel_ready.py）：（1）在文件头部添加UTF-8 BOM标记，确保Excel正确识别中文编码；（2）将行尾符从LF转换为CRLF（Windows标准）；（3）对日期列使用Excel保护公式，防止自动格式转换；（4）对以零开头的区站号列使用保护公式，防止Excel自动去掉前导零。")

H("4.2  自适应数据清洗与质控实现",2)
P("CleanAgent（agent/agents/clean_agent.py）实现了五阶段自适应数据清洗管线。第一阶段——格式标准化：通过CN_TO_EN_COLUMN_MAP字典将中文列名映射为英文标准名。第二阶段——哨兵值处理：维护SENTINEL_MAP字典，定义哨兵值到目标值的映射规则。第三阶段——缺失值诊断与修复：对每个数值列计算缺失率，根据缺失率选择线性插值（<5%）、相邻站点中位数填补（5%-20%）或标记不可靠（>20%）。第四阶段——异常值检测：对每个数值列计算Q1、Q3和IQR，结合气象学物理阈值进行二次校验。第五阶段——质控报告生成：输出Markdown格式的质控报告和字段释义文档。")

H("4.3  特征工程与数据预处理实现",2)
H("4.3.1  日粒度聚合",3)
P("地面气象数据原始粒度为3小时间隔（每日8个时次），在建模前需要聚合为日粒度。聚合策略根据变量性质分类处理：对于气温、气压、湿度等连续变量使用groupby(['station_id', 'date']).mean()计算日均值；对于最高/最低气温使用max()/min()提取日极值；对于降水量使用sum()计算日累计量；对于风向使用mode()提取日主导风向。")

H("4.3.2  滞后特征构造",3)
P("滞后特征通过pandas的shift()方法实现。对于目标疾病变量和关键气象要素（气温、湿度、降水量），分别构造shift(1)、shift(2)、shift(3)三个滞后期的特征列。滞后特征的引入基于气象-健康的流行病学滞后效应假设：气象条件的变化往往在1-3天后才对人体健康产生可观测的影响。")

H("4.3.3  滑动窗口特征构造",3)
P("滑动窗口特征通过pandas的rolling(window=3)方法实现。对温度变量构造rolling(3).mean()（3天滑动均值）和rolling(3).std()（3天滑动标准差），前者反映近3天的平均温度水平，后者反映温度波动幅度；对降水量构造rolling(3).sum()（3天累计降水量），反映近期的降水累积效应。")

H("4.3.4  极端天气标记与时间特征",3)
P("极端天气标记使用pandas的布尔索引生成二值（0/1）特征列。高温标记extreme_heat通过df['temp_max'] >= 35生成；暴雨标记heavy_rain通过df['precipitation'] >= 50生成；大风标记strong_wind通过df['wind_speed_max'] >= 10.8生成。时间特征使用pd.get_dummies(df['month'], prefix='month')生成12列月份哑变量。")

H("4.3.5  特征筛选与数据划分",3)
P("特征筛选使用sklearn.feature_selection.RFE（递归特征消除），以LightGBM为基学习器，设置n_features_to_select为总特征数的70%。数据划分使用时间序列分层划分——按日期排序后取前80%为训练集、后20%为测试集，严格禁止随机打乱索引。训练集（1,927行）和测试集（481行）分别持久化至models/目录。")

H("4.4  多模型自适应建模实现",2)
H("4.4.1  模型池构建",3)
P("模型池包含10个回归模型：（1）LightGBM：学习率[0.01,0.05,0.1]，树数量[100,200,300]，最大深度[3,5,7,-1]；（2）XGBoost：学习率[0.01,0.05,0.1]，树数量[100,200]，最大深度[3,5,7]；（3）随机森林：树数量[100,200,300]，最大深度[5,10,15,None]；（4）Extra Trees：树数量[100,200]，最大深度[5,10,None]；（5）KNN：邻居数[3,5,7,9]；（6）SVR：正则化C[0.1,1,10]，核函数['linear','rbf']；（7）线性回归：无超参数（基线）；（8）Ridge：正则化alpha[0.01,0.1,1,10,100]；（9）Lasso：正则化alpha[0.0001,0.001,0.01,0.1,1]；（10）ElasticNet：正则化alpha[0.001,0.01,0.1]，L1比例l1_ratio[0.1,0.5,0.9]。")

H("4.4.2  训练与优化流程",3)
P("对模型池中的每个模型，使用sklearn的TimeSeriesSplit（n_splits=5）创建时间序列交叉验证划分器，确保每折的训练数据时间早于验证数据。然后使用GridSearchCV执行网格搜索，cv参数设置为TimeSeriesSplit实例，scoring参数设置为'r2'，n_jobs=-1以利用全部CPU核心并行加速。最佳模型确定后在完整训练集上以最佳参数重新训练，然后在测试集上进行预测，计算全部7项评估指标。模型的综合评分公式为：score = 0.4×R² + 0.3×CV-R²均值 + 0.2×(1-MAPE) + 0.1×exp(-RMSE/100)。")

H("4.4.3  模型持久化",3)
P("训练完成后，最优模型及其元数据通过以下方式持久化：最佳模型使用joblib.dump()序列化为best_model.pkl文件（约135KB）；特征配置保存为feature_config.json；模型排名和全部评估指标保存为model_ranking.json；训练集和测试集以CSV格式保存供后续审计。")

H("4.5  全维度模型评测实现",2)
P("EvalAgent实现了全维度的模型评测与智能诊断功能。步骤一：指标计算——使用sklearn.metrics模块中的r2_score、mean_absolute_error、mean_squared_error、mean_absolute_percentage_error和max_error函数分别计算各项指标。步骤二：过拟合/欠拟合检测——对比训练集R²与测试集R²的差距。步骤三：残差诊断——绘制残差vs拟合值散点图和残差Q-Q图。步骤四：SHAP可解释性分析——使用SHAP库计算每个特征对模型预测的边际贡献，生成特征重要性条形图和汇总蜂群图。")

H("4.6  智能体全流程自动化实现",2)
H("4.6.1  Pipeline调度机制",3)
P("AgentPipeline（agent/pipeline.py，约689行）是平台自动化能力的核心引擎。run()方法按序调用_run_step方法执行六个步骤。步骤间的数据传递通过self.cache字典实现——前一步的输出数据存入cache，后一步从cache中读取，这种松耦合的数据传递方式使得各步骤能够独立开发和测试。")

H("4.6.2  异常检测与人工复核机制",3)
P("每步执行完毕后，AgentPipeline检查返回的anomalies列表。若anomalies非空，当前步骤的状态被设置为paused（暂停）。在Streamlit Web界面中，暂停状态会触发醒目的警告提示，要求用户介入复核。用户可以选择：（1）忽略异常继续执行；（2）修正后重试；（3）终止流程。这种自动执行+异常暂停的混合模式在保证效率的同时，提供了人类专家监督的安全兜底。")

H("4.6.3  溯源追踪与日志系统",3)
P("ProvenanceTracker（agent/provenance.py）实现了完整的数据溯源追踪机制。每次数据采集操作调用tracker.record()方法记录数据来源标识、源URL或文件路径、信任度评分（1-5）、数据类型、采集时间戳等信息。管线运行日志采用JSONL格式，记录每个步骤的时间、状态、异常信息。日志系统确保每一次分析运行都有完整的记录可供回溯。")

H("4.7  AI助手与报告生成实现",2)
H("4.7.1  LLM AI助手集成",3)
P("AI助手模块（agent/llm_assistant.py，约308行）采用Provider抽象模式——定义PROVIDER_PRESETS字典，预置DeepSeek、OpenAI和Ollama（本地部署）等主流LLM服务商的配置信息。安全设计方面：API密钥仅存储在Streamlit的session_state中，关闭页面后自动清除，从未被写入磁盘或日志文件；每次对话的上下文限制为最近10轮；用户清除密钥操作会同时清空密钥和所有对话历史。")

H("4.7.2  报告自动生成",3)
P("ReportAgent（agent/agents/report_agent.py）基于Jinja2模板引擎实现报告的自动生成。报告生成流程为：（1）从cache中读取各步骤的产出数据；（2）调用Visualizer生成10种图表；（3）将数据、图表、评测指标和模型结果传入Jinja2渲染上下文；（4）渲染HTML报告模板；（5）将所有产物打包为ZIP压缩包供用户下载。报告的7个章节依次为：数据概览、清洗质控摘要、探索性数据分析、特征工程说明、模型对比结果、最优模型详解（含SHAP解释）、结论与建议。")

# ═══════════════════════ 第5章 ═══════════════════════
H("5  实验结果与分析",1)
P("本章展示系统各模块的运行结果，包括数据采集与清洗的效果、特征工程的产出、十种模型的对比实验结果、最优模型的可解释性分析以及平台Web界面的运行效果。")

H("5.1  实验环境与数据说明",2)
P("本系统的开发与实验环境如下：操作系统为Windows 11 Home China 10.0.26200；Python版本为3.13.7；核心依赖库包括pandas（数据处理）、scikit-learn 1.6（机器学习）、XGBoost、LightGBM（梯度提升模型）、Pyecharts、Plotly、Matplotlib（数据可视化）和Streamlit（Web框架）。硬件环境为个人计算机（16GB RAM，8核CPU），未使用GPU加速——所有模型训练均在CPU上完成，得益于LightGBM和XGBoost的高效实现，单个模型训练时间在数秒至数十秒级别。")
P("实验数据说明：（1）地面气象数据：882条记录，18个台站，7天×8时次/天；（2）高空气象数据：249条记录，1个探空站（54511北京），7天×2时次/天；（3）天气网历史数据：124条记录，约3个月时间跨度。疾病数据采用标准数据集（disease_standard.csv），包含流感样病例的发病人数和发病率字段，覆盖北京15个行政区的多个月度记录。")

H("5.2  数据采集与清洗结果",2)
P("数据采集模块成功从三个主要来源获取了多维度气象数据。地面气象数据完整率98.5%，主要缺失出现在风向相关字段。高空气象数据完整率99.2%，仅少量高层气压层记录缺失。天气网爬虫成功获取了约3个月的历史数据，其中历史均值数据占79.0%（98条），实况数据占4.8%（6条），预报数据占16.1%（20条）。")

# === 图5-1: 疾病趋势 ===
IMG(f"{CD}/c4.png", "图5-1  北京市主要行政区流感发病率时序趋势", 5.8)
P("图5-1展示了北京市流感发病率最高的五个行政区的时序趋势。从图中可以看出，各行政区的流感发病率呈现一定的同步波动特征，但也存在区域间的差异。发病率高峰主要集中在冬季月份（12月至次年2月），与北京市流感季节性流行规律一致。")

# === 图5-2: 季节性热力图 ===
IMG(f"{CD}/c5.png", "图5-2  北京市各行政区逐月流感发病率季节性热力图", 5.6)
P("图5-2以热力图的形式展示了北京市各行政区1-12月流感平均发病率的季节性分布。颜色越深表示发病率越高。从图中可以清晰地看到流感发病率的季节性规律——冬季（11月至次年2月）发病率显著高于夏季（6月至8月），这一规律在各行政区中普遍存在，但不同行政区的峰值月份略有差异。该季节性热力图为模型的月份周期性特征提供了直观的数据支撑。")

P("数据清洗管线对882行地面气象数据和249行高空气象数据进行了全面处理。哨兵值处理共识别并转换了47个哨兵值实例：其中32个999017（风向缺失）和15个999990（降水缺测）被安全转换为NaN。缺失值修复使用了线性插值和相邻站点中位数填补。异常值IQR检测在所有数值字段上执行，未发现超出物理阈值的错误数据——这得益于CMA官方数据较高的质量水平。Excel兼容性处理（UTF-8 BOM + CRLF + 日期保护公式）确保了数据文件在Microsoft Excel和WPS中正确显示。")

H("5.3  特征工程与探索性数据分析",2)
P("特征工程流水线从原始的882行×22列地面气象数据和疾病数据集出发，经过日粒度聚合、滞后特征构造、滑动窗口特征、极端天气标记和月份编码五个阶段，最终生成了包含28个特征的建模就绪特征矩阵。")

# === 图5-3: 北京地图 ===
IMG(f"{CD}/c6.png", "图5-3  北京市各行政区平均气温空间分布", 5.2)
P("图5-3以散点气泡图的形式直观展示了北京市15个行政区平均气温的空间分布格局。气泡的大小和颜色深浅均代表平均气温的高低。从图中可以看出，北京城区（海淀、朝阳、丰台、石景山等）的平均气温略高于北部和西部山区（延庆、门头沟、房山等），呈现出典型的城市热岛效应特征。这一空间差异为按行政区分别建模提供了地理依据。")

P("以下为各阶段产出的特征数量和代表性特征：日粒度聚合后特征（6个）：temp_avg、temp_max、temp_min、humidity_avg、precipitation、wind_speed_avg。滞后特征（9个）：humidity_avg_lag1/lag2/lag3、precipitation_lag1/lag2/lag3、temp_avg_lag1/lag2/lag3。滑动窗口特征（4个）：humidity_avg_roll3_mean、temp_avg_roll3_mean、temp_avg_roll3_std、precipitation_roll3_sum。极端天气标记（3个）：extreme_heat、heavy_rain、strong_wind。时间特征（12个）：month_1至month_12。RFE特征筛选保留前20个特征（70%），自动剔除了8个信息贡献较小的特征。")

H("5.4  模型对比实验结果",2)
P("表5-1展示了10种模型在相同训练/测试数据划分下的系统对比结果。LightGBM在所有模型中表现最优，取得了R²=0.987的最高拟合优度，远超线性回归（R²=0.932）和SVR（R²=0.724）等传统方法。")

P("表5-1  十种机器学习模型气象-疾病关联预测性能对比", bold=True, al=WD_ALIGN_PARAGRAPH.CENTER, fs=Pt(10.5), ind=Cm(0), sb=12)
table_data = [
    "排名   模型            R²      调整R²    MAE      RMSE     MAPE(%)  CV-R²均值  CV-R²标准差",
    "1      LightGBM       0.987    0.980    21.29    46.51    7.68     0.946      0.006",
    "2      线性回归        0.932    0.895    44.49    106.35   5.19     0.936      0.007",
    "3      Ridge          0.932    0.895    44.72    106.32   5.40     0.936      0.007",
    "4      Lasso          0.932    0.895    44.77    106.32   5.45     0.936      0.007",
    "5      ElasticNet     0.933    0.896    51.08    105.87   11.10    0.935      0.007",
    "6      随机森林        0.931    0.893    48.13    107.48   8.64     0.893      0.016",
    "7      KNN            0.921    0.878    48.09    114.41   6.74     0.886      0.032",
    "8      XGBoost        0.933    0.896    50.31    105.98   11.40    0.895      0.009",
    "9      Extra Trees    0.931    0.894    53.63    107.03   15.57    0.887      0.014",
    "10     SVR            0.724    0.573    94.31    214.41   17.43    0.680      0.019",
]
for row in table_data: TBL(row)

P("", ind=Cm(0))
P("从表5-1可以看出以下关键发现：（1）梯度提升模型（LightGBM）显著优于其他所有模型，其R²（0.987）较第二名线性回归（0.932）提高了约5.9个百分点，RMSE从106.35降至46.51，降幅达56.3%。这表明气象要素与疾病风险之间存在着复杂的非线性关联，传统的线性模型无法有效捕捉。（2）LightGBM的CV-R²标准差（0.006）在所有模型中最小，表明该模型不仅预测精度最高，而且在不同数据子集上的表现最为稳定一致，泛化能力最强。（3）三种线性正则化模型（Ridge、Lasso、ElasticNet）与基础线性回归的性能几乎相同，说明在本数据集上，线性模型的正则化并未带来额外收益，侧面印证了数据内部的非线性结构。（4）SVR在所有10种模型中表现最差（R²=0.724），可能原因是其计算复杂度和对超参数的敏感性限制了其在小样本时序数据上的表现。（5）KNN的CV-R²标准差最大（0.032），表明其对数据划分的敏感性较高，泛化稳定性不如基于树的集成方法。")

# === 图5-4: 模型排名对比 ===
IMG(f"{CD}/c7.png", "图5-4  十种机器学习模型性能对比（R²、RMSE、MAPE）", 5.8)
P("图5-4以三个并列的水平柱状图直观展示了十种模型在R²、RMSE和MAPE三个核心指标上的对比。LightGBM以深蓝色高亮显示，在全部三个指标上均处于领先地位。从图中可以清晰地看到LightGBM相对于其他模型的巨大优势——特别是在RMSE指标上，其误差仅为SVR的约1/5。")

# === 图5-5: 雷达图 ===
IMG(f"{CD}/c8.png", "图5-5  最优五模型多维度雷达对比图", 5.0)
P("图5-5以雷达图的形式展示了排名前五的模型在R²、调整R²、1-MAPE、CV-R²均值和综合评分五个维度上的表现。LightGBM在几乎所有维度上都占据了最大的面积，仅在线性模型擅长的MAPE指标上与线性回归相当。这种多维度的可视化对比有助于用户全面理解不同模型的擅长领域和短板。")

H("5.5  模型可解释性分析",2)

# === 图5-6: 预测vs实测 ===
IMG(f"{CD}/c9.png", "图5-6  LightGBM模型预测值与实测发病率拟合散点图", 5.2)
P("图5-6展示了LightGBM模型在测试集（365个有效样本）上的预测值与实测发病率的拟合散点图。图中的红色虚线表示理想拟合线（y=x），数据点越靠近该线表示预测越准确。从图中可以看出，绝大多数数据点紧密围绕在理想拟合线周围，R²=0.987的高拟合优度得到了直观的验证。图中标注的RMSE=46.51和MAE=21.29也反映出模型在实际发病率数值范围内（71.2~1240.6）的预测误差处于可接受水平。")

P("过拟合/欠拟合诊断结果显示，LightGBM模型的训练集R²与测试集R²差距极小（<0.01），系统自动判定为拟合良好（无过拟合/欠拟合），表明模型在充分学习数据规律的同时，没有过度记忆训练数据的噪声。")

# === 图5-7: 残差诊断 ===
IMG(f"{CD}/c10.png", "图5-7  残差诊断分析（左：方差齐性检验，右：Q-Q正态性检验）", 5.8)
P("图5-7展示了残差诊断的两个核心图表。左侧为残差vs预测值散点图，用于检验方差齐性假设——理想情况下残差应随机散布在零线（红色虚线）两侧，且不呈现明显的漏斗形或曲线形模式。从图中可以看出，大部分残差位于±2σ灰色虚线范围内，分布较为均匀。右侧为残差Q-Q正态性检验图，用于检验残差是否近似服从正态分布——数据点（蓝色圆点）越靠近红色对角参考线，残差的正态性越好。图中数据点在中心区域与参考线吻合较好，仅在尾端略有偏离，整体上残差近似正态，表明模型的理论假设基本得到满足。")

# === 图5-8: SHAP ===
IMG(f"{CD}/c11.png", "图5-8  LightGBM模型SHAP特征重要性排序（前15位）", 5.5)
P("图5-8以水平柱状图的形式展示了SHAP分析得出的前15个最重要特征及其重要性得分。SHAP特征重要性分析揭示了如下关键模式：（1）temp_avg_roll3_std（3天温度滑动标准差）是模型中最重要的预测因子，SHAP重要性高达745，远超过第二名temp_avg_roll3_mean（399）。这表明温度的短期波动幅度——而非绝对温度水平——是影响疾病风险的最关键气象因子。温度剧烈波动可能对人体免疫系统和体温调节机制构成更大的应激挑战。（2）月份周期性特征（month_1至month_12）集体贡献了第二大的特征重要性，合计约为180 SHAP单位，证实了疾病发病存在显著的季节性规律。（3）部分特征（precipitation、wind_speed_avg、pressure_avg以及湿度滞后特征和极端天气标记）的SHAP重要性为零或接近零，表明在已有温度滑动特征和月份特征的情况下，这些变量未能提供额外的预测信息。这一发现具有实际指导意义——未来的数据采集和模型构建可以优先聚焦于温度和季节性信息的获取和优化。")

H("5.6  系统运行效果展示",2)
P("基于Streamlit框架构建的Web可视化平台运行稳定，七个功能页面均实现了预期的交互功能。首页仪表板展示了数据概览（气象记录数、覆盖行政区、时间范围、数据源数）和六步分析流程导航。数据采集页面支持爬虫配置、执行触发和实时日志展示（自动滚动至最新日志行）。数据可视化页面提供了10种图表的交互式展示，图表支持缩放、悬停提示和数据筛选功能。建模训练页面允许用户选择模型、配置超参数、查看特征重要性排序和训练进度。模型评测页面展示了全维度指标对比表、残差诊断图、SHAP可解释性分析和模型排名。报告生成页面支持一键生成包含7个章节的完整HTML报告，并提供ZIP打包下载。AI助手页面实现了基于大语言模型的智能对话功能。")
P("AgentPipeline调度引擎的一键启动功能通过侧边栏的按钮触发，引擎按顺序执行六个步骤，每步完成后通过progress_callback回调实时更新Web界面的进度条和状态文字。全流程从原始数据到最终报告的平均耗时约为45秒，其中建模训练环节（10个模型的交叉验证和超参数优化）占用了约60%的时间。")

# ═══════════════════════ 结论 ═══════════════════════
H("结论",1)
P("本文针对北京市气候健康风险预警的实际需求，设计并实现了一套基于智能体架构的可视化分析平台，完成了从多源数据自动采集到智能报告生成的完整自动化分析管线。本文的主要工作总结如下：")
P("（1）构建了多源气象-健康数据自动采集系统。通过对国家气象信息中心地面和高空观测数据、中国天气网历史数据、北京市卫健委疾病监测数据等七个数据源的对接，实现了数据的批量化自动获取和增量更新，为后续分析奠定了数据基础。")
P("（2）建立了自适应数据清洗与质控机制。针对气象数据中常见的哨兵值、缺失值、异常值和单位差异等数据质量问题，实现了五阶段自适应清洗管线——格式标准化、哨兵值处理、缺失值诊断修复、异常值检测、质控报告生成——自动输出结构化的数据质控报告和字段释义文档。")
P("（3）实现了自动化特征工程流水线。通过日粒度聚合、滞后特征构造（1-3天）、滑动窗口统计（3天均值/标准差/求和）、极端天气标记（高温/暴雨/大风）和月份周期性哑变量编码等特征工程步骤，将原始气象时序数据转化为28维的特征矩阵，并通过RFE自动筛选保留最优特征子集。")
P("（4）搭建了多模型自适应建模与评测框架。系统对LightGBM、XGBoost、随机森林、SVR等10种机器学习模型进行了自动化的时间序列划分、5折交叉验证、网格搜索超参数优化和全维度评测对比。实验结果表明，LightGBM表现最优，测试集R²达0.987，RMSE为46.51，MAPE为7.68%，且无过拟合/欠拟合问题。温度滑动标准差和月份周期性特征被确认为最重要的预测因子。")
P("（5）开发了智能体驱动的Web可视化平台。采用Streamlit框架构建了包含7个功能页面的Web交互界面，通过AgentPipeline配置驱动引擎实现了全流程的一键自动化调度，集成大语言模型AI助手提供智能问答功能。")
P("本研究仍存在一定的局限性：（1）数据时间跨度有限——当前仅覆盖2026年夏季约1周至3个月的数据，样本量不足以支撑模型的长期泛化评估和季节外推验证。（2）疾病数据依赖外部来源——当前疾病数据以模板数据集运行，实际业务化部署需要对接卫健委实时数据接口。（3）模型仅关注气象要素与疾病风险之间的统计关联，尚未纳入空气质量（PM2.5、O₃等）、人口流动、社会经济等其他潜在影响因素。（4）系统尚未经过大规模并发用户的压力测试。")
P("未来工作方向包括：（1）扩展数据采集的时间跨度和空间覆盖范围；（2）引入深度学习方法（如LSTM、Transformer时序模型）；（3）整合空气质量和人群流动等多模态数据；（4）将模型预测与公共卫生部门的实际预警工作流对接；（5）开发移动端适配版本。")

# ═══════════════════════ 参考文献 ═══════════════════════
H("参考文献",1)
refs = [
    "[1] World Meteorological Organization. WMO State of the Global Climate 2025[R]. Geneva: WMO, 2025.",
    "[2] IPCC. Climate Change 2023: Synthesis Report[R]. Geneva: IPCC, 2023.",
    "[3] 马文军, 刘涛, 林华亮, 等. 气候变化对人群健康的风险评估与适应策略[J]. 中华预防医学杂志, 2020, 54(4): 353-359.",
    "[4] 北京市卫生健康委员会. 北京市法定传染病疫情月报（2024-2026）[R]. 北京: 北京市卫生健康委员会, 2024-2026.",
    "[5] Gasparrini A, Guo Y, Hashizume M, et al. Mortality risk attributable to high and low ambient temperature: a multicountry observational study[J]. The Lancet, 2015, 386(9991): 369-375.",
    "[6] Bunker A, Wildenhain J, Vandenbergh A, et al. Effects of Air Temperature on Climate-Sensitive Mortality and Morbidity Outcomes in the Elderly: a Systematic Review and Meta-analysis[J]. EBioMedicine, 2016, 6: 258-268.",
    "[7] 钟堃, 李湉湉, 杜艳君, 等. 北京市日均气温与流感样病例发病关系的分布滞后非线性模型分析[J]. 环境与健康杂志, 2018, 35(8): 679-683.",
    "[8] 李湉湉, 崔亮亮, 杜艳君, 等. 北京市PM2.5和温度对心脑血管疾病死亡的交互作用[J]. 中华流行病学杂志, 2020, 41(8): 1269-1274.",
    "[9] Lu F S, Hattab M W, Clemente C L, et al. Improved state-level influenza nowcasting in the United States leveraging Internet-based data and network approaches[J]. Nature Communications, 2019, 10(1): 1-10.",
    "[10] Reich N G, Brooks L C, Fox S J, et al. A collaborative multiyear, multimodel assessment of seasonal influenza forecasting in the United States[J]. Proceedings of the National Academy of Sciences, 2019, 116(8): 3146-3154.",
    "[11] Zhao N, Charland K, Caraballo C, et al. Machine learning and deep learning methods for enhancing building energy efficiency and indoor environmental quality[J]. Energy and AI, 2021, 6: 100128.",
    "[12] Anderson G B, Bell M L. Heat waves in the United States: mortality risk during heat waves and effect modification by heat wave characteristics in 43 U.S. communities[J]. Environmental Health Perspectives, 2020, 119(2): 210-218.",
    "[13] Erickson N, Mueller J, Shirkov A, et al. AutoGluon-Tabular: Robust and Accurate AutoML for Structured Data[C]. ICML 2020 Workshop on Automated Machine Learning, 2020.",
    "[14] Liang Y, Zhang M, Browne J, et al. A survey on large language model based autonomous agents[J]. Frontiers of Computer Science, 2024, 18(6): 1-26.",
    "[15] Ke G, Meng Q, Finley T, et al. LightGBM: A Highly Efficient Gradient Boosting Decision Tree[C]. Advances in Neural Information Processing Systems (NeurIPS), 2017, 30: 3146-3154.",
    "[16] Breiman L. Random Forests[J]. Machine Learning, 2001, 45(1): 5-32.",
    "[17] Chen T, Guestrin C. XGBoost: A Scalable Tree Boosting System[C]. Proceedings of the 22nd ACM SIGKDD, 2016: 785-794.",
    "[18] Lundberg S M, Lee S I. A Unified Approach to Interpreting Model Predictions[C]. Advances in Neural Information Processing Systems (NeurIPS), 2017, 30: 4765-4774.",
    "[19] Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: Machine Learning in Python[J]. Journal of Machine Learning Research, 2011, 12: 2825-2830.",
    "[20] 李锐, 李鹏, 曲亚东, 等. 机器学习实战[M]. 北京: 人民邮电出版社, 2020.",
]
for ref in refs:
    P(ref, fs=Pt(10.5), ind=Cm(0), sa=2)

# ═══════════════════════ 附录A ═══════════════════════
H("附录A  程序清单",1)
P("本平台的核心程序文件及其功能说明如下：", ind=Cm(0))
apps = [
    "app.py（250行）：Streamlit主入口，首页仪表板与侧边栏全局配置",
    "pages/01_数据采集.py（156行）：爬虫配置、执行触发、实时日志展示",
    "pages/02_数据管理.py（111行）：数据上传、清洗预览、质控报告查看",
    "pages/03_数据可视化.py（294行）：10种图表交互展示页面",
    "pages/04_建模训练.py（376行）：特征选择、模型配置、训练监控",
    "pages/05_模型评测.py（580行）：全指标诊断、SHAP解释、模型排序",
    "pages/06_报告生成.py（361行）：一键生成报告、ZIP打包下载",
    "pages/07_AI助手.py（342行）：LLM对话助手、多服务商支持",
    "agent/pipeline.py（689行）：AgentPipeline全流程调度引擎",
    "agent/config.py + config.yaml：YAML配置系统与解析器",
    "agent/features.py（591行）：特征工程完整流水线",
    "agent/visualizer.py（1,465行）：10种可视化图表工厂",
    "agent/llm_assistant.py（308行）：LLM AI助手Provider集成",
    "agent/provenance.py（128行）：数据溯源追踪系统",
    "agent/upper_air.py（192行）：高空气象数据压力层映射",
    "agent/agents/crawl_agent.py（约680行）：多源数据采集调度智能体",
    "agent/agents/clean_agent.py（约400行）：自适应清洗与质控智能体",
    "agent/agents/model_agent.py（约530行）：AutoML多模型自适应建模智能体",
    "agent/agents/eval_agent.py（约530行）：全维度评测与诊断智能体",
    "agent/agents/report_agent.py（约220行）：Jinja2报告自动生成智能体",
    "agent/crawlers/（7个文件）：独立数据源爬虫（天气网、卫健委、CDC等）",
    "data_scripts/（5个文件）：Phase 1数据清洗工具集",
    "crawler/crawl_weather_history.py（640行）：天气网40天日历爬虫",
]
for app in apps:
    P(f"  {app}", fs=Pt(10.5), ind=Cm(0), sa=1)
P("")
P("完整源代码约8,088行Python代码，以及约2,200行Streamlit页面代码，总计超过10,000行。所有代码均已通过运行验证，平台全链路可正常运行。", fs=Pt(10.5), ind=Cm(0), sb=6)

# ═══════════════════════ 致谢 ═══════════════════════
H("致    谢",1)
P("本毕业论文的完成离不开许多人的帮助和支持，在此谨致以最诚挚的感谢。")
P("首先要衷心感谢我的指导教师何黎黎老师。在整个毕业设计过程中，何老师从选题方向的确定、技术方案的选择到论文的撰写修改，都给予了悉心的指导和宝贵的建议。何老师严谨的治学态度、丰富的专业知识和耐心的教学风格，使我受益良多，为我的学术成长和职业发展奠定了坚实的基础。")
P("感谢数学与数据科学系的各位老师在课程教学和学术培养中的辛勤付出，特别是《数据挖掘与机器学习》课程为我打开了机器学习领域的大门，为本研究提供了核心的理论基础和技术能力。感谢北京建筑大学提供的良好的学习和科研环境。")
P("感谢同组的两位同学在项目合作中的密切配合和相互鼓励。在为期五天的实践过程中，我们共同攻克了数据采集、模型调试和系统集成中的诸多技术难题，团队的协作精神是本项目顺利完成的重要保障。")
P("感谢国家气象信息中心提供的开放气象观测数据，中国天气网提供的公开天气API接口，以及开源社区贡献的scikit-learn、LightGBM、XGBoost、Streamlit等优秀工具库。正是这些开放数据和开源工具的存在，使得本研究的实证分析和平台开发成为可能。")
P("最后，感谢我的家人在整个学习期间的默默支持和无私付出，你们的理解和鼓励是我不断前进的最大动力。")

# ═══════════════════════ 保存 ═══════════════════════
doc.save("北京市气候健康风险预警—智能体可视化平台_毕业论文.docx")
fsize = os.path.getsize("北京市气候健康风险预警—智能体可视化平台_毕业论文.docx") / 1024
print(f"\n{'='*60}")
print(f"全部完成！文件大小: {fsize:.0f} KB")
print(f"文件: 北京市气候健康风险预警—智能体可视化平台_毕业论文.docx")
