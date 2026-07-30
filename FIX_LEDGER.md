# 综合修复任务账本

- 目标：修复 `CODE_REVIEW.md` 已确认的问题，并完成可重复验收。
- 分支：`fix/comprehensive-review-remediation`
- 范围：
  - 历法与梅花易数时间起卦。
  - API 请求模型、错误边界和前后端调用链。
  - 纳甲、生克重复/失效实现及空模块。
  - CORS、启动脚本、文档、UI、测试与 CI。
- 已确认事实：
  - `main` 基线提交为 `68c162c`，已推送到 `origin/main`。
  - 远程仓库此前为空。
  - 修复分支已建立；审查报告列出 4 项 P1、8 项 P2、9 项 P3。
  - 历法采用 `lunar-python==1.4.8`、八字 `sect=2`（民用午夜换日），
    年月柱按精确节气时刻切换。
  - 时间起卦采用农历月日、年支和时支序数，不再使用公历年月日数字。
  - `64gua_full.json` 与权威八宫生成表逐项一致，纳甲运行时以该文件为
    唯一六十四卦来源，经卦纳支使用地支步长 2。
  - 生克模块的冲合、三合筛选已明确为“项目展示口径”，不再冒充无流派
    差异的唯一古法。
  - 前端不再维护六十四卦名映射，卦辞、爻辞改由后端按卦名查询。
- 决策：
  - 使用唯一、可测试的领域实现，删除运行时 monkey patch 和重复模型。
  - 使用精确历法依赖，明确时间与子时约定。
  - 保持现有页面功能和主要 API 路径兼容，非法输入改为稳定 4xx。
  - 每个关键阶段单独提交。
- 修改文件：
  - 第一阶段：`backend/core/ganzhi.py`、`backend/core/meihua.py`、
    `backend/api/qigua.py`、`backend/api/paipan.py`、
    `backend/models/gua.py`、`backend/core/liuyao_engine.py`、
    `requirements*.txt`、`pyproject.toml`、`tests/test_ganzhi.py`、
    `tests/test_meihua.py`、`tests/test_qigua_api.py`。
  - 第二阶段：`backend/core/najia.py`、`backend/core/shengke.py`、
    `backend/core/liuyao_engine.py`、`backend/core/guaci.py`、
    `backend/api/cidian.py`、`backend/models/gua.py`、
    `backend/models/request.py`、`tests/test_najia.py`、
    `tests/test_shengke.py`、`tests/test_engine_regression.py`、
    `tests/test_cidian.py`。
  - 第三阶段：`frontend/js/config.js`、`frontend/js/utils.js`、
    `frontend/js/qigua.js`、`frontend/js/paipan.js`、
    `frontend/index.html`、`frontend/css/style.css`、
    `frontend/favicon.svg`、`backend/core/guaci.py`、
    `backend/api/cidian.py`、`tests/test_cidian.py`、
    `tests/test_frontend_contract.py`。
- 验证结果：
  - 第一阶段 25 项历法、梅花起卦、概率映射和 API 契约测试通过。
  - 第一阶段新增/重写文件 Ruff 检查通过，`git diff --check` 通过。
  - 第二阶段全套 41 项测试通过；其中覆盖 64 卦静态数据及全部 4,096
    种本卦/动爻组合。
  - 第二阶段相关文件 Ruff 检查及 `git diff --check` 通过。
  - 第三阶段全套 45 项测试、Node.js 全部脚本语法检查、相关 Ruff 与
    `git diff --check` 通过。
  - 真实 Chromium 已通过自动、指定时间、手工指定、六次手摇四条流程；
    网络记录确认分别调用对应起卦接口及排盘接口，422 失败会显示在
    `aria-live` 状态区，浏览器控制台无错误。
- 验收门槛：
  - 单元、API、前端静态检查全部通过。
  - 64 卦数据与 4,096 种本卦/动爻组合回归通过。
  - 真实浏览器四种起卦流程及失败路径通过。
  - 历法权威样本和梅花易数原典样本通过。
- 剩余风险：六爻流派差异需以文档明确，不以未取证规则冒充统一标准。
- 下一步：收紧 CORS 与服务配置，统一启动脚本，补齐依赖锁定、CI、
  项目文档及剩余低优先级清理。
