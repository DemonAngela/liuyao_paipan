# 周易六爻排盘系统

[![CI](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/test.yml/badge.svg)](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/test.yml)
[![CodeQL](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/codeql.yml/badge.svg)](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个把六爻传统规则编码为**可检查、可测试、可复现软件**的开源项目。仓库提供 Python 集成接口、FastAPI REST API、浏览器界面、六十四卦结构化数据、回归测试、Docker 发布和规则来源/约定文档。

> **状态：持续维护、pre-1.0。** 项目用于学习、研究、软件验证与可复现的规则讨论，不宣称是传统术数的唯一权威解释，也不应用于医疗、法律、金融等高风险决策。

## 已实现

- 三枚铜钱 6/7/8/9 概率起卦
- 手动摇卦与手工指定六爻
- 纳甲、六亲、世应、六神、旬空
- 动爻、变卦与部分生克冲合关系
- 六十四卦与 384 条爻辞数据
- 基于真实节气交接时刻的可复现干支年月边界
- 小型、稳定的 Python 集成接口
- FastAPI REST API 与原生 JavaScript 前端
- 与稳定规则契约明确区分的实验性时间起卦接口

## 快速开始

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m backend.main
```

访问 `http://127.0.0.1:8000`，交互式 API 文档位于 `/docs`。

### Python 集成

```python
from backend import calculate_ganzhi, paipan

ganzhi = calculate_ganzhi(1986, 5, 29, 0, 0)
chart = paipan(
    [1, 1, 1, 1, 1, 1],
    year=2026,
    month=4,
    day=23,
    hour=10,
)
```

稳定集成入口与输入约定见 [`docs/PYTHON_API.md`](docs/PYTHON_API.md)。

### Docker

```bash
docker build -t liuyao-paipan .
docker run --rm -p 8000:8000 liuyao-paipan
```

版本发布会生成 GHCR 镜像；Release workflow 同时生成容器 SBOM、provenance 与针对镜像 digest 的 GitHub artifact attestation。

## 干支历法基准

生产代码固定使用 `lunar_python==1.4.8` 作为**可复现的软件基准**。年柱与月柱使用该基准计算的真实节气交接时刻；项目明确采用晚子时 `23:00-23:59` 不提前换日的 `Exact2 / sect-2` 约定。

这是一项确定的软件工程约定，不代表某个库或某个术数流派具有普遍唯一权威。规则来源、争议处理和验证范围见 [`docs/VALIDATION.md`](docs/VALIDATION.md) 与 [`docs/SOURCES_AND_SCOPE.md`](docs/SOURCES_AND_SCOPE.md)。

CI 对这部分至少验证：

- 人工可读的固定参考案例
- 2020–2029 年 1 月跨年边界样本
- 2024–2026 年十二个“节”交接前后各 1 分钟
- 晚子时换日约定
- 2020–2029 共 3,653 个每日正午样本，年/月/日柱对固定基准必须保持 **0 mismatch**

## 更广泛的自动验证

Pull Request 会运行：

- Python 3.10 / 3.11 / 3.12
- 后端编译检查
- 安装后 Python 公共 API import/调用检查
- pytest 回归与 HTTP smoke tests
- Docker image build
- CodeQL 安全分析

测试还覆盖输入边界、三枚铜钱映射、64 卦/384 爻数据完整性、实际 HTTP 路径、Python 公共接口，以及 **64 个本卦 × 64 个动爻 mask = 4,096 种组合**的结构化排盘验证。

Dependabot 持续维护 Python 与 GitHub Actions 依赖。领域规则变更需要可复现案例，并附可核验来源/参考实现或明确的项目约定。

## 已知限制

1. **时间起卦仍是实验性实现。** `/api/qigua/time` 当前使用简化公历数字算法，不宣称已经实现有完整出处的传统年月日时起例；Issue #2 持续跟踪。
2. **部分旺衰、生克与暗动规则仍属于工程化简化。** 在形成更多有出处的固定案例前，不做更强兼容性声明。
3. **纳甲/参考数据的重复事实来源仍需继续收敛。** Issue #4 跟踪唯一可审计事实来源。
4. **深层语义回归仍在扩展。** 4,096 条引擎路径已自动结构验证；Issue #5 继续补世应、纳甲、六亲、六神与动变关系的来源型预期值。

## 维护与贡献

- [`MAINTAINERS.md`](MAINTAINERS.md) — 维护职责与决策规则
- [`ROADMAP.md`](ROADMAP.md) — 可靠性与互操作路线图
- [`CHANGELOG.md`](CHANGELOG.md) — 兼容性/安全变更
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — 贡献与测试要求
- [`SECURITY.md`](SECURITY.md) — 漏洞报告方式
- [`docs/RELEASING.md`](docs/RELEASING.md) — 可重复发布流程
- [`docs/MAINTAINER_AUTOMATION.md`](docs/MAINTAINER_AUTOMATION.md) — PR review、issue triage、测试和发布自动化边界
- [`docs/VALIDATION.md`](docs/VALIDATION.md) — 回归与基准验证策略

Codex 对该仓库最有价值的维护工作包括：PR 影响分析、Issue 复现、回归测试草拟、规则/数据一致性检查、文档与 API 一致性检查、依赖/安全审查和 Release 准备。任何 AI 产出仍需维护者审核，且 AI 输出本身不能作为传统规则正确性的证据。

欢迎提交 bug、可核验规则出处、回归案例、文档改进、可访问性修复和真实集成。项目只记录真实公开采用度，不制造 Star、Fork、下载或互动。

## License

[MIT License](LICENSE)
