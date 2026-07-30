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
- 验证结果：
  - 第一阶段 25 项历法、梅花起卦、概率映射和 API 契约测试通过。
  - 第一阶段新增/重写文件 Ruff 检查通过，`git diff --check` 通过。
- 验收门槛：
  - 单元、API、前端静态检查全部通过。
  - 64 卦数据与 4,096 种本卦/动爻组合回归通过。
  - 真实浏览器四种起卦流程及失败路径通过。
  - 历法权威样本和梅花易数原典样本通过。
- 剩余风险：六爻流派差异需以文档明确，不以未取证规则冒充统一标准。
- 下一步：修复纳甲、生克关系、重复模型和运行时 monkey patch，并完成
  64 卦及 4,096 种组合回归。
