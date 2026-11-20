# 北京市气候健康风险预警 — 智能体可视化平台 使用说明报告

> 📅 生成时间：2026-07-14 | 版本：v2.1
>
> 面向角色：数据分析师 / 公共卫生研究员 / 气象业务人员

---

## 目录

1. [系统概述](#一系统概述)
2. [快速启动](#二快速启动)
3. [Web平台操作指南](#三web平台操作指南)
4. [命令行工具](#四命令行工具)
5. [爬虫模块详解](#五爬虫模块详解)
6. [配置文件说明](#六配置文件说明)
7. [数据管线详解](#七数据管线详解)
8. [接口契约](#八接口契约)
9. [验证与质量保证](#九验证与质量保证)
10. [常见问题](#十常见问题)

---

## 一、系统概述

### 1.1 项目定位

一个**全流程自动化智能体平台**，覆盖"数据采集 → 清洗质控 → 特征工程 → 自适应建模 → 多维度评测 → 报告生成"的完整管线。用户通过 Web UI 配置参数后一键启动，智能体自动执行，仅在数据异常或模型失效时触发人工复核。

### 1.2 技术栈

| 层 | 选型 | 说明 |
|----|------|------|
| Web界面 | **Streamlit** | 单进程全栈，6 个功能页面 |
| 图表 | **Pyecharts** + **Plotly** + **Matplotlib** | 地图/热力/时序/3D散点/SHAP/残差诊断 |
| 建模 | **scikit-learn** + **XGBoost** + **LightGBM** | 10 模型池 + PyCaret 降级模式 |
| 调度引擎 | **自定义 AgentPipeline** | YAML 驱动，6 步顺序执行 + 异常暂停 |
| 报告 | **Jinja2** → HTML/Markdown | 7 章完整报告 + ZIP 打包 |
| 配置 | **YAML** (PyYAML) | 人类可读写 |

### 1.3 项目文件结构

```
项目根目录/
├── app.py                          # Streamlit 入口（首页仪表板）
├── pages/                          # 6 个 Web 功能页面
│   ├── 01_数据采集.py               # 爬虫配置 + 执行 + 实时日志
│   ├── 02_数据管理.py               # 数据上传 + 清洗预览 + 质控报告
│   ├── 03_数据可视化.py             # 10 种图表（地图/趋势/关联/诊断）
│   ├── 04_建模训练.py               # 特征选择 + 模型对比 + 训练监控
│   ├── 05_模型评测.py               # 全指标 + 残差诊断 + SHAP + 排序
│   └── 06_报告生成.py               # 一键生成报告 + ZIP/HTML 下载
│
├── agent/                          # 智能体核心
│   ├── pipeline.py                 # AgentPipeline 调度引擎
│   ├── config.py + config.yaml     # 配置系统
│   ├── provenance.py               # 数据溯源追踪
│   ├── features.py                 # 特征工程
│   ├── visualizer.py               # 10 种图表工厂
│   ├── agents/
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
├── crawler/                        # Phase 1 天气网爬虫
├── output/                         # 标准化数据产出
├── raw/                            # 原始采集数据
├── models/                         # 训练好的模型文件
├── reports/                        # 生成的报告
├── logs/                           # 结构化 JSON 日志 + 溯源记录
├── templates/report.md.j2          # 报告 Jinja2 模板
├── scripts/verify_all.py           # 全平台数据核验脚本
└── CLAUDE.md                       # 项目 AI 协作规则
```

---

## 二、快速启动

### 2.1 环境要求

| 组件 | 最低版本 | 验证命令 |
|------|---------|---------|
| Python | 3.10+ | `python --version` |
| pip | 22.0+ | `pip --version` |

### 2.2 安装依赖

```bash
# 核心依赖（必需）
pip install streamlit pandas numpy requests beautifulsoup4 lxml openpyxl

# 机器学习（必需）
pip install scikit-learn xgboost lightgbm scipy statsmodels shap

# 可视化（必需）
pip install pyecharts plotly matplotlib seaborn

# 报告和配置（必需）
pip install jinja2 pyyaml

# AutoML（可选，不可用时自动降级到 sklearn）
pip install pycaret
```

### 2.3 启动 Web 平台

```bash
cd 机器学习实践任务三
streamlit run app.py
```

浏览器访问 **http://localhost:8501** 即可进入平台首页。

### 2.4 一键验证

```bash
python scripts/verify_all.py
```

预期输出：`✅ 全部核验通过！错误=0 警告=0`

---

## 三、Web平台操作指南

### 首页 — 项目仪表板

侧边栏配置区：

| 参数 | 说明 | 可选值 |
|------|------|--------|
| 目标行政区 | 多选 | 北京 18 个区 |
| 疾病类型 | 下拉选择 | 法定传染病(总计) / 流感 / 手足口病 等 |
| 年份范围 | 滑动条 | 2020-2026 |
| 一键启动 | 按钮 | 触发完整管线 |

主页展示区：项目概述 → 数据状态卡片 → 6 页快速导航

---

### 页面 01 — 数据采集

```
操作流程：
1. 在左侧面板勾选目标数据源（支持多选）
2. 点击「启动采集」
3. 右侧实时日志区逐行显示采集进度
4. 采集完成后显示数据摘要（行数/站数/时间范围）
```

可用数据源：

| 数据源 | 模块 | 预计数据量 | 耗时 |
|--------|------|:--:|:--:|
| 中国天气网 40 天 API | weather_history | ~120 行/月 | ~4s/月 |
| 天气后报网历史实况 | tianqihoubao | ~30 行/月 | ~3s/月 |
| CMA 数据门户 | cma_portal | 取决于注册状态 | 10s |
| 北京市卫健委 | bj_health_commission + beijing_health_data | ~13 月报 | ~30s |
| 中国 CDC / 国家卫健委 | china_cdc | 取决于反爬 | 30s+ |
| 文献数据提取 | literature_extract | 取决于 raw/ 文件 | 5s |

---

### 页面 02 — 数据管理

```
功能：
- 上传外部 CSV/Excel 文件（支持拖拽）
- 数据预览表（可翻页、排序、筛选）
- 列名模糊匹配 + 手动映射 → 统一到标准 Schema
- 质控报告查看：缺失率统计 / 异常值标记 / 哨兵值处理记录
- 清洗前后的对比视图
```

---

### 页面 03 — 数据可视化

10 种图表，每种支持独立筛选（时间范围、行政区）：

| # | 图表 | 工具 | 用途 |
|---|------|------|------|
| 1 | 气象变量时序折线图 | Pyecharts Line | 查看温度/湿度/风速逐日变化 |
| 2 | 疾病趋势图 | Pyecharts Bar + Line | 传染病发病数月际变化 |
| 3 | Spearman 相关热力图 | Pyecharts HeatMap | 气象-疾病关联强度 |
| 4 | 北京区划风险等级地图 | Pyecharts Map(北京) | 空间分布一目了然 |
| 5 | 温-湿-风 3D 散点图 | Plotly 3D Scatter | 三维交互探索 |
| 6 | 疾病季节性热力图 | Pyecharts HeatMap | 月×区 疾病分布 |
| 7 | SHAP 特征重要性 | SHAP + Plotly | 模型解释 |
| 8 | 残差诊断四联图 | Matplotlib | QQ/分布/Learning Curve/预测vs真实 |
| 9 | 模型对比雷达图 | Plotly Radar | 多模型多维比较 |
| 10 | 模型排名条形图 | Pyecharts Bar | 综合得分排序 |

---

### 页面 04 — 建模训练

```
自适应决策树（自动选择最佳策略）：
├── 数据量 < 50 行  → 仅线性回归（模型仅供参考）
├── 数据量 50-200   → Linear + Ridge + Lasso + DecisionTree
├── 数据量 200-1000 → 全模型池 + 5-Fold CV + RFE 特征筛选
└── 数据量 > 1000   → 全模型池 + 10-Fold CV + 全超参数搜索

操作：
1. 选择目标变量（incidence / cases）
2. 确认特征列表（可手动增删）
3. 调整测试集比例（默认 20%）
4. 点击「开始训练」
5. 右侧显示：训练进度条 + 各模型 R² 实时对比 + 最优模型高亮
```

---

### 页面 05 — 模型评测

全维度指标展示：

| 类别 | 指标 | 说明 |
|------|------|------|
| 拟合精度 | MAE, MSE, RMSE, R², Adjusted R² | 标准回归指标 |
| 百分比误差 | MAPE, SMAPE | 排除 y=0 的情况 |
| 极端误差 | Max Error, Median Absolute Error | 最坏情况评估 |
| 残差分析 | Shapiro-Wilk 正态性, Breusch-Pagan 异方差 | 模型假设检验 |
| 泛化能力 | K-Fold CV R²(mean±std), Learning Curve | 过拟合检测 |
| SHAP | TreeExplainer → Linear → Kernel 回退链 | 特征重要性解释 |

自动诊断：
- Train R² - Test R² > 0.1 → ⚠️ 过拟合警告
- Train R² + Test R² 均 < 0.5 → ⚠️ 欠拟合警告

---

### 页面 06 — 报告生成

```
操作：
1. 勾选报告内容：嵌入图表 / 附带数据集 / 附带模型文件
2. 选择输出格式：HTML / Markdown
3. 点击「生成分析报告」
4. 下载：HTML 报告 + ZIP 全量包

报告章节（7 章）：
  一、数据概况 — 气象/疾病数据统计摘要
  二、数据质控 — 缺失率/哨兵值/异常值处理记录
  三、特征工程 — 构造逻辑 + 重要性预排名
  四、模型结果 — 最优模型参数 + 对比排名表
  五、模型评测 — 全指标 + 诊断结论 + 残差图
  六、可视化   — 内嵌 PNG 图表
  七、数据溯源 — 每条数据来源/时间/信任度

历史报告浏览：reports/ 目录下按时间戳归档
```

---

## 四、命令行工具

### 4.1 全平台验证

```bash
python scripts/verify_all.py
```

核验 5 大类：
1. 气象数据：行数校验 + 物理范围 + 原始数据交叉验证（温差 ≤0.01°C）
2. 高空数据：气压层完整性 + 温度递减检查
3. 疾病数据：月度覆盖 + 季节性模式（冬季>夏季）
4. 溯源系统：记录数 + 可用建模比例
5. 文件完整性：30 个必要文件逐一检查

### 4.2 单独运行采集器

```bash
# CMA 数据门户（检测可用性 + 生成注册指南）
python agent/crawlers/cma_portal.py

# 处理从 CMA 下载的原始数据文件
python agent/crawlers/cma_portal.py --process <文件路径>

# 中国 CDC / 国家卫健委
python agent/crawlers/china_cdc.py

# 北京市卫健委综合采集
python agent/crawlers/beijing_health_data.py

# 天气后报网历史实况
python agent/crawlers/tianqihoubao.py

# 天气网 40 天 API
python agent/crawlers/weather_history.py

# 北京市卫健委疫情公告
python agent/crawlers/bj_health_commission.py

# 文献 PDF/Excel 表格提取
python agent/crawlers/literature_extract.py
```

### 4.3 运行完整智能体管线

```bash
# 不启用爬虫（仅加载已有数据 → 标准化）
python agent/agents/crawl_agent.py

# 在 Python 中调用
python -c "
from agent.agents.crawl_agent import CrawlAgent
agent = CrawlAgent()
agent.run_full(enable_crawlers=True)  # 启用实时爬虫
"
```

---

## 五、爬虫模块详解

### 5.1 模块一览

| 模块 | 文件 | 数据源 | 信任度 | 状态 |
|------|------|------|:--:|:--:|
| 中国天气网 | `weather_history.py` | d1.weather.com.cn 日历 API | 2~3 | ✅ 可用 |
| 天气后报网 | `tianqihoubao.py` | tianqihoubao.com 历史天气 | 3 | ✅ 可用 |
| CMA 数据门户 | `cma_portal.py` | data.cma.cn 国家气象中心 | 5 | ⚠️ 需注册 |
| 北京市卫健委 | `bj_health_commission.py` | wjw.beijing.gov.cn 公告 | 3 | ✅ 可用 |
| 北京疾病综合 | `beijing_health_data.py` | 卫健委 + CDC + 公卫中心 | 3~4 | ✅ 可用 |
| 中国 CDC | `china_cdc.py` | chinacdc.cn + nhc.gov.cn | 4 | ⚠️ 有反爬 |
| 文献提取 | `literature_extract.py` | raw/ 目录中的 PDF/Excel | 1 | ✅ 可用 |

### 5.2 CMA 数据门户（cma_portal.py）

```
运行行为：
1. 检测本地已有 CMA 文件（Phase 1 产物）
2. 探测 8 个 CMA 门户页面可访问性
3. 尝试公开数据接口
4. 生成 raw/CMA_数据获取指南.md（含 18 站列表 + 注册流程）

命令行：
  python agent/crawlers/cma_portal.py                    # 检测+生成指南
  python agent/crawlers/cma_portal.py --process <文件>   # 处理下载的原始数据
```

### 5.3 中国 CDC（china_cdc.py）

```
运行行为：
1. 尝试国家卫健委疫情月报页面
2. 尝试北京 CDC 站点
3. 解析 39 种甲乙丙类法定传染病分病种数据
4. 全部失败时生成 raw/CDC_数据获取指南.md

已知限制：
  - 国家卫健委有 WAF（Web应用防火墙），返回 HTTP 412
  - 北京 CDC 有 SSL 证书问题
  - 建议手动下载 PDF 后用 literature_extract.py 提取
```

### 5.4 北京疾病综合采集器（beijing_health_data.py）

```
三个数据源：
  源1: 北京市卫健委 (wjw.beijing.gov.cn)
       → 月度法定传染病报告页面
       → 提取总病例数 + 死亡数 + 主要病种
  源2: 北京疾控中心 (bjcdc.org.cn)
       → SSL 证书问题，备用
  源3: 公共卫生科学数据中心 (phsciencedata.cn)
       → 公开数据集下载

输出文件：
  raw/beijing_disease_monthly.csv      — 原始采集
  output/disease_standard.csv          — 标准接口契约格式
```

---

## 六、配置文件说明

### 6.1 管道配置（agent/config.yaml）

```yaml
pipeline:
  data:
    sources:                          # 启用的数据源
      - CMA_SURF_OBS                  # CMA 地面观测（信任度 5）
      - CMA_UPAR_OBS                  # CMA 高空探空（信任度 5）
      - WEATHER_COM                   # 中国天气网（信任度 2~3）
      - TIANQIHOUBAO                  # 天气后报网（信任度 3）
      - BJ_HEALTH_COMM               # 北京市卫健委（信任度 3）
      - CHINA_CDC                     # 中国 CDC（信任度 4）

  model:
    target: incidence                 # 建模目标变量
    test_size: 0.2                    # 测试集比例
    cv_folds: 5                       # 交叉验证折数
    metric: r2                        # 模型筛选指标

  evaluation:
    overfit_threshold: 0.1            # 过拟合阈值（Train R² - Test R²）
    underfit_threshold: 0.5           # 欠拟合阈值（两者均低于此值）

  report:
    format: html                      # 报告格式：html / markdown
    include_charts: true              # 是否嵌入图表
    include_data: true                # 是否附带数据集
```

### 6.2 数据源信任度体系

| 信任度 | 来源 | 说明 |
|:--:|------|------|
| 5 | CMA 官方实测 | 国家气象信息中心原始观测，最高权威 |
| 4 | 国际数据库 | NOAA GSOD/ISD，WHO 数据 |
| 3 | 政府公开报告 | 卫健委/CDC 公报，天气网实况 |
| 2 | 第三方实况 | 天气网历史均值，天气后报网 |
| 1 | 文献提取 | 论文附表/补充材料 |
| 0 | 未知来源 | 临时数据 |
| -1 | 预报数据 | **不入建模**，仅趋势参考 |

---

## 七、数据管线详解

### 7.1 完整数据流

```
┌─────────────────────────────────────────────────────────────────┐
│                        AgentPipeline                            │
│                                                                 │
│  Step 1          Step 2         Step 3        Step 4 & 5       │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌───────────┐    │
│  │CrawlAgent│ → │CleanAgent│ → │ Feature  │ → │ModelAgent │    │
│  │         │    │         │    │Engineer  │    │EvalAgent  │    │
│  │ 多源采集 │    │ 自适应   │    │ 特征工程 │    │ 建模+评测 │    │
│  │ 标准化   │    │ 清洗质控 │    │ 时间聚合 │    │ 模型排序 │    │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └─────┬─────┘    │
│       │               │               │                 │        │
│       ▼               ▼               ▼                 ▼        │
│  weather_standard  质控报告     特征矩阵            best_model   │
│  disease_standard  (Markdown)   (训练/测试)        ranking.json │
│       │                                                         │
│       └─────────────────┬───────────────────────┘               │
│                         ▼                                        │
│                    Step 6                                        │
│                  ┌──────────┐                                    │
│                  │ReportAgent│ → 报告 + ZIP                      │
│                  └──────────┘                                    │
│                                                                 │
│  异常触发规则（人工复核介入）:                                    │
│  • 数据源全部失败 → 提示手动上传                                 │
│  • 缺失率 > 50%  → 建议排除该区                                  │
│  • 模型 R² < 0   → 提示特征不足/数据量不足                       │
│  • 异常值 > 10%  → 提示确认数据质量                              │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 核心输出文件

| 文件 | 行数 | 列数 | 时间范围 | 说明 |
|------|:--:|:--:|------|------|
| `weather_standard.csv` | 126 | 12 | 2026-07-05~11 | CMA地面日聚合，18站 |
| `upper_air_standard.csv` | 249 | 14 | 2026-07-05~11 | CMA高空探空，19气压层 |
| `disease_standard.csv` | 98 | 8 | 2024-12~2026-06 | 真实北京月度传染病 |
| `weather_com_reference.csv` | 124 | 9 | 2026-04~08 | 天气网参考（不入建模） |
| `数据质控报告.md` | — | — | — | 6 章节质控分析 |

---

## 八、接口契约

### 契约 A：Agent A → Agent B/C（数据传递）

`output/weather_standard.csv`：

| 列名 | 类型 | 说明 |
|------|------|------|
| station_id | str | 区站号（5位） |
| district | str | 行政区（中文） |
| date | str | 日期 YYYY-MM-DD |
| temp_avg | float | 日均温 ℃ |
| temp_max | float | 日最高温 ℃ |
| temp_min | float | 日最低温 ℃ |
| humidity_avg | float | 日均相对湿度 % |
| precipitation | float | 日降水量 mm |
| wind_speed_avg | float | 日均风速 m/s |
| pressure_avg | float | 日均气压 hPa |
| source_trust | int | 信任度 -1~5 |
| provenance_id | str | 溯源标识 |

`output/disease_standard.csv`：

| 列名 | 类型 | 说明 |
|------|------|------|
| district | str | 行政区 |
| year | int | 年份 |
| month | int | 月份 |
| disease_type | str | 疾病类型 |
| incidence | float | 发病率(/10万) |
| cases | int | 发病数 |
| source_trust | int | 信任度 -1~5 |
| provenance_id | str | 溯源标识 |

### 契约 B：Agent B → Agent C（模型传递）

| 文件 | 格式 | 内容 |
|------|------|------|
| `models/best_model.pkl` | pickle | sklearn 兼容模型对象 |
| `models/model_ranking.json` | JSON | 最优模型 + 全指标 + 特征重要性 + 诊断 |
| `models/feature_config.json` | JSON | 特征列表 + 目标变量 + 划分参数 |

---

## 九、验证与质量保证

### 9.1 自动核验清单

运行 `python scripts/verify_all.py` 执行 5 大类检查：

| # | 核验项 | 方法 | 阈值 |
|---|--------|------|:--:|
| 1 | 气象数据完整性 | 行数 = 126，列数 = 12 | 精确匹配 |
| 2 | 气象-原始交叉验证 | 逐行比对 CMA 原始日均温 | 温差 ≤ 0.01°C |
| 3 | 物理范围 | temp[-50,55], humidity[0,100], pressure[850,1100] | 不得有违规值 |
| 4 | 高空温度递减 | 地面温度 > 高层温度 | 必须递减 |
| 5 | 疾病季节性 | 冬季(11-2月)均值 > 夏季(6-8月)均值 | 呼吸道疾病模式 |
| 6 | 溯源覆盖 | 记录数 > 1000 | 每条数据有源可查 |
| 7 | 文件完整性 | 30 个必要文件逐一检查 | 不得缺失 |

### 9.2 数据真实性保障

- ✅ 所有数据记录通过 `provenance_id` 字段可追溯到源文件/URL
- ✅ 质控报告列出每个数据源的信任度等级
- ✅ 报告中**无**「模拟数据」「合成数据」字样
- ✅ 缺失字段标注「数据不可用」而非填充假值
- ✅ 天气预报数据标记 `source_trust = -1`，不进入建模训练

### 9.3 已知数据限制

| # | 限制 | 影响 | 缓解措施 |
|---|------|------|---------|
| 1 | CMA 地面数据仅 7 天（2026-07-05~11） | 训练样本不足，模型仅供参考 | 注册 CMA 获取更长时序；使用天气后报网扩展 |
| 2 | 疾病数据为市级总量，无分区分病种 | 无法做空间精细化建模 | 标注限制，留出数据上传接口 |
| 3 | 天气网数据全部为预报值（obs=0） | 无法作为建模输入 | 已标记 trust=-1，仅作参考 |
| 4 | CMA 数据门户需注册 | 新用户无法直接获取 API 数据 | 已生成注册指南 `raw/CMA_数据获取指南.md` |
| 5 | CDC/卫健委网站有反爬 | 自动采集不稳定 | 已生成替代方案指南 `raw/CDC_数据获取指南.md` |

---

## 十、常见问题

### Q1: Streamlit 启动后浏览器打开白屏？

```bash
# 检查端口是否被占用
netstat -ano | findstr 8501

# 换个端口启动
streamlit run app.py --server.port 8502
```

### Q2: 某爬虫运行后无数据？

查看对应日志文件（`logs/crawl_*.log`）和说明文件（`raw/*_note.txt`）。大多数情况是被反爬/网站改版，对应的指南文件提供了手动替代方案。

### Q3: 如何添加新的数据源？

1. 在 `agent/crawlers/` 中按现有模式编写新爬虫（`crawl(output_dir)` 函数签名为标准接口）
2. 在 `agent/agents/crawl_agent.py` 的 `run_crawlers()` 中注册
3. 在 `agent/config.yaml` 的 `pipeline.data.sources` 中添加源名称

### Q4: 模型 R² 很低怎么办？

这是数据量不足的预期表现（当前仅 7 天地面数据 + 13 月市级疾病数据）。建议：
- 通过 CMA 获取更长时间序列的气象数据
- 上传更多年份的疾病数据
- 平台会自动检测并标注「数据量不足，模型仅供参考」

### Q5: 如何确保数据真实性？

平台的溯源系统（`provenance.py`）保证每条数据记录都标注了来源 URL 和获取时间，质控报告中有完整的溯源统计章节。运行 `python scripts/verify_all.py` 可以检查溯源覆盖度。

### Q6: PyCaret 安装失败怎么办？

系统内置了 sklearn 降级模式，PyCaret 不可用时自动回退到：
- `sklearn.model_selection.GridSearchCV` 做超参数搜索
- 手动 10 模型池逐一训练 + 对比
- 功能等价，不影响建模效果

### Q7: 高空数据和地面数据有什么区别？

| | 地面观测 | 高空探测 |
|------|------|------|
| 台站数 | 18 个（覆盖北京各区） | 1 个（54511 北京站） |
| 物理含义 | 地表气温/湿度/风/气压 | 各气压层(1000→3hPa)的温度/风/高度 |
| 时间粒度 | 每 3 小时（8 时次/天） | 每 12 小时（00/12 UTC） |
| 输出文件 | `weather_standard.csv` | `upper_air_standard.csv` |
| **严禁混合** | ⚠️ 500hPa 的 -18°C 与地面 +27°C 不能放在同一个「温度」列取平均 |

---

## 附录 A：全部命令速查

```bash
# === 启动平台 ===
streamlit run app.py

# === 验证 ===
python scripts/verify_all.py

# === 数据采集 ===
python agent/crawlers/cma_portal.py              # CMA 门户检测 + 指南
python agent/crawlers/china_cdc.py               # CDC/卫健委
python agent/crawlers/beijing_health_data.py     # 北京疾病数据
python agent/crawlers/tianqihoubao.py            # 天气后报网
python agent/crawlers/weather_history.py         # 天气网 40 天 API
python agent/crawlers/bj_health_commission.py    # 北京市卫健委
python agent/crawlers/literature_extract.py      # 文献提取

# === 智能体管线 ===
python agent/agents/crawl_agent.py               # 数据标准化
python agent/agents/clean_agent.py               # （通过 pipeline 调用）
python agent/agents/model_agent.py               # （通过 pipeline 调用）

# === 配置文件 ===
# agent/config.yaml  — 管道参数
# agent/config.py    — 接口契约列定义
```

## 附录 B：产出文件速查

| 目录 | 用途 | 关键文件 |
|------|------|---------|
| `output/` | 标准化数据集 | `weather_standard.csv`, `disease_standard.csv`, `数据质控报告.md` |
| `raw/` | 原始采集数据 | `beijing_disease_monthly.csv`, `CMA_数据获取指南.md` |
| `models/` | 训练产物 | `best_model.pkl`, `model_ranking.json`, `feature_config.json` |
| `logs/` | 运行日志 + 溯源 | `provenance.json`, `crawl_*.log`, `clean_*.log` |
| `reports/` | 生成的报告 | 按时间戳归档的 HTML + MD + ZIP |
