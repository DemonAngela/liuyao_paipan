# 周易六爻排盘系统 项目维护手册

## 一、项目概述
本项目是一个基于《增删卜易》专家经验的六爻排盘 Web 应用，提供自动起卦、手动摇卦、时间起卦、手工指定等多种方式，并自动完成纳甲、装六亲、安世应、配六神、查旬空、推生克冲合等全套排盘流程，同时支持卦辞爻辞查询。

**核心特点：**
- 严格遵循传统六爻排盘规则，采用预置六十四卦全量表保证准确性
- 前后端分离架构，后端提供 RESTful API，前端纯静态页面
- 支持 Windows 环境一键启动，开发与维护便捷

## 二、技术栈与部署
- 后端框架：Python 3 + FastAPI  
- Web服务器：Uvicorn（支持热重载）  
- 前端：HTML + CSS + 原生 JavaScript（无框架依赖）  
- 数据存储：JSON 文件（卦辞、爻辞、六十四卦元数据）  
- 依赖管理：requirements.txt  
- 启动命令：`python -m backend.main` 或双击 `start.bat`  
- 监听地址：`host="0.0.0.0"`，端口 8000，支持 IPv4 与 IPv6（双栈）  
- 静态文件：前端目录 `frontend/` 直接挂载到根路径

## 三、目录结构说明
```
liuyao_paipan/
├── backend/                     # 后端根目录
│   ├── main.py                  # FastAPI 主入口，路由注册，静态文件挂载，CORS 配置
│   ├── api/                     # API 路由层
│   │   ├── __init__.py
│   │   ├── qigua.py             # 起卦相关接口（自动/手动/指定/时间）
│   │   ├── paipan.py            # 排盘接口（调用引擎）
│   │   └── cidian.py            # 卦辞、爻辞查询接口
│   ├── core/                    # 核心算法模块
│   │   ├── __init__.py
│   │   ├── ganzhi.py            # 干支历法计算（年月日时干支、旬空）
│   │   ├── liuyao_engine.py     # 排盘总引擎（整合所有子模块）
│   │   ├── liushen.py           # 六神排布（根据日干）
│   │   ├── xunkong.py           # 旬空标注
│   │   └── shengke.py           # 生克冲合计算（六合、六冲、三合、生旺墓绝、日月关系、暗动等）
│   ├── models/                  # Pydantic 数据模型（请求/响应/内部数据）
│   │   └── gua.py               # YaoDataModel、GuaDataModel、QiguaRequest 等
│   ├── utils/                   # 工具与常量
│   │   └── constants.py         # 五行、地支关系、纳甲表、特殊卦属性等
│   └── data/                    # 静态数据文件（需预生成）
│       ├── 64gua_full.json      # 六十四卦完整元数据（卦宫、世应、各爻地支六亲，由脚本生成）
│       ├── 64gua.json           # 卦辞、彖辞、象辞
│       └── yaoci.json           # 384 爻爻辞
├── frontend/                    # 前端静态资源
│   ├── index.html               # 主页面
│   ├── css/
│   │   └── style.css            # 样式表
│   └── js/
│       ├── config.js            # API 基础 URL（动态同源）
│       ├── utils.js             # 工具函数（阴阳符号、格式化等）
│       ├── qigua.js             # 起卦交互逻辑（含手工指定面板）
│       └── paipan.js            # 排盘结果渲染、爻辞悬停、关系面板
├── scripts/                     # 辅助脚本
│   └── generate_64gua_table.py  # 六十四卦元数据生成脚本（最终修正版）
├── requirements.txt             # Python 依赖清单
├── start.bat                    # Windows 一键启动脚本
└── README.md                    # 项目说明
```

## 四、核心算法模块详解

### 4.1 干支历法 (`ganzhi.py`)
- **功能**：根据公历年月日时计算年、月、日、时干支，并推导旬空。
- **关键函数**：  
  `get_ganzhi_by_date(year, month, day, hour)` → 返回字典包含 year/month/day/hour 干支及 xunkong 元组。  
  `get_xunkong(day_ganzhi)` → 返回空亡两地支。
- **节气处理**：年以立春为界，月以节气为界，使用五虎遁/五鼠遁定干。

### 4.2 六十四卦元数据 (`64gua_full.json`)
- **内容**：每卦的宫属、世应、各爻地支和六亲（预计算）。
- **生成方式**：运行 `scripts/generate_64gua_table.py`，基于权威八宫卦列表和纳甲表生成。
- **更新机制**：修改 `GONG_GUA_LIST` 后重新运行脚本，覆盖 JSON 文件。

### 4.3 排盘引擎 (`liuyao_engine.py`)
- **类 `LiuyaoEngine`**：  
  - `paipan(qigua_result)` → 输入起卦数据，返回 `GuaData` 对象。  
  - 流程：查表获取本卦变卦信息 → 获取干支旬空 → 配六神 → 计算伏神 → 动变爻处理 → 日月关系 → 冲合关系 → 卦属标记 → 组装结果。
- **伏神计算**：若本卦六亲不全，仅当本宫同位爻的六亲属于缺失六亲时才显示伏神，否则不显示。  
- **动变关系**：回头生、回头克、化合、化冲，根据变爻与本爻的生克冲合判断。  
- **日月关系**：值（相同地支）、临（五行同、地支不同）、生、合、冲、克、月破、暗动/日破（见下文）。
- **卦属性标记**：通过 `SPECIAL_GUA` 常量判断六冲、六合、归魂、游魂。

### 4.4 生克冲合计算 (`shengke.py`)
- **类 `ShengKeCalculator`**：  
  - `find_liuhe(yao_list)` / `find_liuchong(yao_list)`：六合/六冲，要求**两爻中至少一爻发动（明动或暗动）**。  
  - `find_sanhe(dizhi_list)`：识别三合局（仅地支组合，未校验动爻条件）。  
  - `calc_shengwangmujue_for_yao(...)`：生旺墓绝状态（基于日月建）。  
  - `calc_riyue_status(yao, ri_ganzhi, yue_ganzhi)`：为单个爻计算所有日月关系（值、临、合、冲、生、克、月破、暗动/日破）。  
  - `_is_wang_single(wuxing, yue_zhi)`：简化旺衰判断（临月建或得月建生扶为旺）。

**暗动/日破判断规则**（已修正）：
1. 静爻逢日冲。  
2. 若爻月破，则直接为日破（月破逢冲更破）。  
3. 若非月破：  
   - 旺相（得月建生/临/值）为暗动；  
   - 休囚（被月建克/无生扶）为日破。  
4. 旬空之爻逢冲：旺则暗动（冲空则实），休囚仍为日破。

### 4.5 数据模型 (`models/gua.py`)
- `YaoDataModel`：包含爻位、六神、六亲、地支五行、旬空、伏神、日月关系字段、动变数据、关系字符串等。  
- `GuaDataModel`：包含本/变卦名、爻列表、世应、干支、旬空、全局关系、卦属性标记。  
- `QiguaRequest` / `QiguaResponse`：起卦请求与响应模型。

### 4.6 前端模块
- **`config.js`**：`API_BASE = window.location.origin`，确保前后端同源。  
- **`qigua.js`**：起卦方式切换、手工指定面板（上爻到初爻排列，按钮默认棕色高亮，点击后切换橄榄绿）。  
- **`paipan.js`**：  
  - 渲染排盘表格（状态列整合世应、旬空、日月关系、暗动/日破、动爻符号）。  
  - 悬停爻辞（本卦/变卦分别请求对应爻辞）。  
  - 全局关系面板（三合局、六合六冲，显示爻位）。  
  - 卦名特殊标记追加。  
- **样式**：`.kong-sign` 红色小字；`.ganzhi-info` 背景圆角；表格列对齐定制。

## 五、API 接口清单
| 路由前缀 | 方法 | 端点 | 功能 |
|----------|------|------|------|
| `/api/qigua` | POST | `/auto` | 自动起卦（随机六爻含动爻） |
| `/api/qigua` | POST | `/manual_step` | 手动摇卦单步 |
| `/api/qigua` | POST | `/manual_complete` | 手动摇卦完成（提交6次结果） |
| `/api/qigua` | POST | `/specify` | 手工指定起卦 |
| `/api/qigua` | POST | `/time` | 时间起卦（梅花易数规则） |
| `/api/paipan` | POST | `/` | 核心排盘（返回完整 GuaData） |
| `/api` | GET | `/guaci/{gua_id}` | 获取指定卦的卦辞、彖辞、象辞 |
| `/api` | GET | `/yaoci/{gua_id}/{yao_pos}` | 获取指定卦指定爻的爻辞 |

## 六、重要数据文件格式
### `64gua_full.json`
```json
{
  "1": {
    "name": "乾为天",
    "gong": "乾",
    "shi": 6, "ying": 3,
    "yao_list": [
      { "pos": 1, "yin_yang": 1, "dizhi": "子", "liuqin": "子孙" }, ...
    ]
  }, ...
}
```

### `64gua.json` / `yaoci.json`
分别为卦辞和爻辞的纯文本数据，结构简单。修改后无需重启服务（文件读取未缓存）。

## 七、维护指南
### 7.1 修改卦辞/爻辞
直接编辑 `backend/data/64gua.json` 和 `yaoci.json`，保持 JSON 结构不变，即时生效。

### 7.2 调整六十四卦核心数据
1. 修改 `scripts/generate_64gua_table.py` 中的 `GONG_GUA_LIST` 或纳甲表。  
2. 运行 `python scripts/generate_64gua_table.py`，确保验证通过。  
3. 将生成的 `64gua_full.json` 复制到 `backend/data/` 覆盖原文件。  
4. 重启后端服务。

### 7.3 前端 UI 调整
- 布局/样式：修改 `style.css` 对应类。  
- 表格列显示逻辑：修改 `paipan.js` 中的 `renderPaipan` 函数。  
- 起卦交互：修改 `qigua.js`。

### 7.4 新增特殊卦标记
在 `backend/utils/constants.py` 的 `SPECIAL_GUA` 字典中补充卦名和属性，刷新页面即可显示。

### 7.5 更改暗动/冲合规则
- 冲合条件修改：在 `shengke.py` 的 `find_liuhe` / `find_liuchong` 中调整 `dong1 or dong2` 逻辑。  
- 暗动判断：修改 `calc_riyue_status` 中的旺衰判断部分。

### 7.6 启动与调试
- 启动：`python -m backend.main`，默认 `http://127.0.0.1:8000`。  
- 热重载：代码修改后自动重启（开发模式）。  
- 查看日志：控制台输出请求错误和伏神调试信息（可去除）。  
- 跨域：已配置 CORS，允许所有来源。

## 八、常见问题排查
| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| 排盘报错“未找到匹配的卦象” | `64gua_full.json` 数据错误或缺失 | 重新生成 JSON 并覆盖 |
| 前端样式丢失/JS 404 | 静态文件路径错误 | 检查 `frontend` 目录位置及 `main.py` 中的静态文件挂载 |
| 旬空不显示红色小字 | 状态列未正确使用 `kong-sign` 类 | 查看 `paipan.js` 中旬空部分是否正确应用 `<span class="kong-sign">` |
| 六合六冲未限制动爻 | `shengke.py` 中方法未接收爻对象列表 | 确保 `find_liuhe` 接收 `yao_list` 而非 `dizhi_list` |
| 伏神全显示 | 六亲齐全判断失效 | 检查 `_get_fushen_for_yao` 中的六亲集合比较逻辑 |
| 变卦爻辞错误 | 悬停事件未区分本卦/变卦 | 确认 `tdBen` 和 `tdBian` 分别监听各自的 `mouseenter` |

此手册基于当前最终版本编写，后续功能扩展请同步更新本文档。