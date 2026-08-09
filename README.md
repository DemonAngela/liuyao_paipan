# 周易六爻排盘系统

一个使用 Python / FastAPI 与原生 JavaScript 实现的开源六爻排盘 Web 应用。项目将六十四卦、纳甲、六亲、六神、旬空、生克冲合等规则编码为可检查、可测试的软件，并提供 REST API 与浏览器界面。

> **项目状态：持续维护中。** 当前实现适合学习、研究与软件工程验证，不应被视为传统术数规则的唯一权威实现，也不应用于医疗、法律、金融等高风险决策。

## 功能

- 自动起卦：按三枚铜钱的 6/7/8/9 概率生成六爻
- 手动摇卦与手工指定六爻
- 实验性时间起卦
- 纳甲、六亲、世应、六神、旬空
- 动爻、变卦与部分生克冲合关系
- 六十四卦卦辞与 384 条爻辞查询
- FastAPI REST API + 无框架静态前端

## 技术栈

- Python 3.10+
- FastAPI / Uvicorn / Pydantic
- HTML / CSS / Vanilla JavaScript
- JSON 静态数据
- pytest + GitHub Actions

## 快速开始

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m backend.main
```

默认访问：`http://127.0.0.1:8000`

如需跨域访问 API，请显式配置允许来源：

```bash
LIUYAO_CORS_ORIGINS=http://localhost:5173,https://example.com
```

默认不开放跨域。

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/qigua/auto` | 三枚铜钱概率自动起卦 |
| POST | `/api/qigua/manual_step` | 返回单爻摇卦结果 |
| POST | `/api/qigua/manual_complete` | 提交完整六爻结果 |
| POST | `/api/qigua/specify` | 指定六爻与动爻 |
| POST | `/api/qigua/time` | 实验性时间起卦 |
| POST | `/api/paipan/` | 根据起卦结果排盘 |
| GET | `/api/guaci/{gua_id}` | 查询卦辞 |
| GET | `/api/yaoci/{gua_id}/{yao_pos}` | 查询爻辞 |

FastAPI 启动后可通过 `/docs` 查看交互式 API 文档。

## 数据与算法

主要实现位于：

```text
backend/
├── api/                 # HTTP API
├── core/                # 干支、排盘、生克等核心逻辑
├── data/                # 64 卦、384 爻及排盘元数据
├── models/              # Pydantic 请求/响应模型
└── utils/               # 常量与辅助逻辑
frontend/                # 浏览器界面
 tests/                  # 回归与数据完整性测试
```

CI 会至少验证：

- 起卦请求的六爻长度、0/1 值域和日期边界
- 三枚铜钱 6/7/8/9 到阴阳/动静的映射
- `64gua_full.json` 包含 64 卦和 384 爻结构
- `yaoci.json` 包含 64 × 6 条非空爻辞
- 后端代码可以完成 Python 编译检查

运行测试：

```bash
pip install pytest
python -m pytest -q
```

## 已知限制

项目主动公开尚未解决的准确性与工程问题，详见 [`CODE_REVIEW.md`](CODE_REVIEW.md)。其中最重要的限制包括：

1. **干支历法边界仍需加强。** 当前节气边界与月柱实现尚未达到精确天文历法级别，交节时刻和跨年边界需要权威历法基准测试。
2. **`/api/qigua/time` 仍是实验性简化实现。** 当前使用公历年月日时数字求和取余，不等同于完整传统《梅花易数》年月日时起例。
3. **部分旺衰、生克与暗动规则属于工程化简化。** 在形成权威决策表和足够基准案例前，不宣称完全覆盖所有传统流派规则。
4. **测试覆盖仍在扩充。** 现有 CI 主要覆盖输入契约和静态数据完整性，下一阶段重点是历法、世应/纳甲、动变和关系计算的基准回归。

公开这些限制是维护策略的一部分：宁可保留可复现的已知问题，也不以无法验证的“绝对准确”描述替代测试证据。

## 维护与贡献

欢迎提交问题、测试案例、传统规则出处、数据纠错和代码改进。贡献前请阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md)。涉及安全问题请按 [`SECURITY.md`](SECURITY.md) 提交。

特别欢迎以下贡献：

- 精确节气/干支历法基准与交界测试
- 可引用来源的纳甲、世应、六亲和动变案例
- API 边界、属性测试和回归测试
- 前端错误处理与可访问性改进
- 文档、英文说明与复现案例

## 开源维护原则

- 规则变化应附可复现案例或来源
- 核心算法修改应同时增加测试
- 已知限制公开记录，不隐藏失败案例
- 安全默认优先，公网部署需显式配置跨域来源
- AI 辅助代码或文档仍需由维护者审查并通过 CI

## License

本项目采用 [MIT License](LICENSE)。
