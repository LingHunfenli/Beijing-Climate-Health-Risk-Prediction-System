# 项目状况报告

> 📅 生成时间：2026-07-14 | 自动检测，实时更新

---

## 一、项目概要

| 项目 | 说明 |
|------|------|
| **名称** | 北京市气候健康风险预警 — 智能体可视化平台 |
| **阶段** | Phase 2+3 平台层完成，全链路可运行 |
| **数据来源** | 国家气象信息中心（地面+高空）、中国天气网、北京市卫健委（月报） |

---

## 二、环境依赖

| 组件 | 版本 | 状态 |
|------|------|:--:|
| Python | 3.13.7 | ✅ |
| Node.js | 24.18.0 | ✅ |
| requests | — | ✅ |
| beautifulsoup4 | 4.14.3 | ✅ |
| lxml | — | ✅ |
| pyright (LSP) | — | ❌ 未安装 |
| typescript-language-server | — | ❌ 未安装（JS 项目才需要） |

---

## 三、Harness 工程体系

| 项目 | 状态 |
|------|:--:|
| **成熟度级别** | L2 核心（开箱即用） |
| **模板版本** | 1.0.0 |
| **健康检查** | 15/18 通过 |

### Hook 注册

| Hook | 时机 | 文件 | 状态 |
|------|------|------|:--:|
| PreToolUse | 工具执行前 | `pre-tool-check.mjs` | ✅ 已注册 |
| SessionStart | 会话开始 | `session-context.mjs` | ✅ 已注册 |
| Stop | 响应结束 | `session-review.mjs` | ✅ 已注册 |
| PostToolUse | 编辑完成后 | `post-tool-check.mjs` | 🔧 未启用 |
| PreCompact | 压缩前 | `pre-compact.mjs` | 🔧 未启用 |

### Skills 包

| Skill | 用途 |
|-------|------|
| `harness-init` | AI 安装向导 |
| `harness-mode` | 工作模式切换（full / hotfix / tweak） |
| `harness-start` | 项目四步初始化 |
| `harness-gc` | GC 自治扫描（8 维健康检查） |
| `tech-review` | 技术方案审查 |
| `verify-goal` | 目标验证 |

---

## 四、数据管线

### 4.1 地面气象数据清洗

| 指标 | 数值 |
|------|------|
| 脚本 | `data_scripts/clean_surface_weather.py` |
| 输入 | `中国地面基本气象观测数据/S202607131155563976300.txt` |
| 输出 | `output/surface_weather_clean_excel_ready.csv` |
| 数据量 | **882 行 × 22 列**（含城市名称列） |
| 台站数 | 18 个（全北京） |
| 时间范围 | 2026-07-05 ~ 2026-07-11（7 天） |
| 观测频率 | 每日 8 时次（0/3/6/9/12/15/18/21） |

**字段（22 列）**：区站号, 城市名称, 年, 月, 日, 时次, 气压, 海平面气压, 最高气压, 最低气压, 最大风速, 极大风速, 极大风速的风向, 2分钟平均风向, 2分钟平均风速, 最大风速的风向, 温度/气温, 最高气温, 最低气温, 相对湿度, 最小相对湿度, 过去3小时降水量

**哨兵值处理**：`999017`→NaN(风向), `999990`→NaN(降水), `999.x`→保留原值(气压)

### 4.2 高空气象数据清洗

| 指标 | 数值 |
|------|------|
| 脚本 | `data_scripts/clean_upper_air.py` |
| 输入 | `中国高空基本气象观测数据/S202607131155563976301.txt` |
| 输出 | `output/upper_air_weather_clean_excel_ready.csv` |
| 数据量 | **249 行 × 19 列**（含城市名称列） |
| 台站数 | 1 个（54511 北京） |
| 时间范围 | 2026-07-05 ~ 2026-07-11（7 天） |
| 观测频率 | 每日 2 时次（00/12 UTC 探空） |

**字段（19 列）**：区站号, 城市名称, 年, 月, 日, 时, 垂直探测意义, 气球施放时间, 时间偏差, 纬度偏差, 经度偏差, 气压, 位势高度, 风向, 风速, 温度/气温, 露点温度, 温度露点差, 规定气压层

**探空分层**：地面层 (EVSS=131072) + 标准气压层 (EVSS=65536, 1000~1hPa)

### 4.3 天气网气候数据爬取

| 指标 | 数值 |
|------|------|
| 脚本 | `crawler/crawl_weather_history.py` |
| 输出 | `output/weather_history_3m_excel_ready.csv` |
| 数据量 | **124 行 × 7 列** |
| 时间范围 | 2026-04-26 ~ 2026-08-01（约 3 个月） |
| 数据源 | 天气网日历 API (calendar_new) + 7天/15天 HTML 解析 |

**字段（7 列）**：日期, 最高气温, 最低气温, 降水概率, 降水量, 数据类型, 数据来源

**三种数据类型**：
| 类型 | cla 映射 | 记录数 | 优先级 |
|------|---------|:--:|:--:|
| 历史均值 | `history` | 98 | 2（最低） |
| 实况 | `obs` | 6 | 0（最高） |
| 预报 | `d15`/`d40` | 20 | 1 |

### 4.4 Excel 兼容性

所有输出 CSV 均已通过 `data_scripts/make_excel_ready.py` 处理：

| 检查项 | 状态 |
|--------|:--:|
| UTF-8 BOM | ✅ 三文件均含 `\xef\xbb\xbf` |
| CRLF 行尾 | ✅ Windows 标准 |
| 日期保护 (`="YYYY-MM-DD"`) | ✅ 全部日期列锁定 |
| ID 保护 (`="区站号"`) | ✅ 防止前导零丢失 |

---

## 五、辅助工具

| 脚本 | 功能 |
|------|------|
| `data_scripts/clean_surface_weather.py` | 地面气象 TAB 清洗 → 中文 CSV |
| `data_scripts/clean_upper_air.py` | 高空探空 TAB 清洗 + 气压层映射 |
| `data_scripts/add_city_column.py` | 区站号 → 城市名称 自动填充（18 站映射表） |
| `data_scripts/make_excel_ready.py` | Excel/WPS 兼容 CSV（BOM + 日期锁定 + CRLF） |
| `data_scripts/fix_csv_encoding.py` | 通用编码修复工具 |
| `crawler/crawl_weather_history.py` | 天气网 40 天日历爬虫 + 多类型去重 |

---

## 六、已知问题 & 待办

| # | 问题 | 影响 | 建议 |
|---|------|------|------|
| 1 | `pyright` LSP 未安装 | IDE 无 Python 类型检查 | `npm install -g pyright` |
| 2 | `package.json` 缺失 (Python 项目) | 健康检查误报，无实际影响 | 忽略 |
| 3 | 项目非 git 仓库 | SessionStart 无法注入 git 状态 | `git init` |
| 4 | 数据仅覆盖 7 天（2026-07-05~11） | 训练样本不足 | 等待更多原始数据 |
| 5 | 天气网爬虫依赖实时 API 可用性 | 下次运行可能失败 | 增加本地缓存降级 |
| 6 | Harness 健康检查 3 项未通过 | LSP 相关，不影响核心功能 | 仅关注 15/18 已通过项 |

---

## 七、快速命令

```bash
# 运行地面数据清洗
python data_scripts/clean_surface_weather.py

# 运行高空数据清洗
python data_scripts/clean_upper_air.py

# 运行天气网爬虫
cd crawler && python crawl_weather_history.py

# Excel 兼容处理
python data_scripts/make_excel_ready.py output/surface_weather_clean.csv

# Harness 健康检查
node scripts/check.mjs

# GC 自治扫描
node scripts/gc-scan.mjs
```

---

> 📝 此文件由 Harness SessionStart 自动注入，每次对话开始时可获取最新项目状态。
