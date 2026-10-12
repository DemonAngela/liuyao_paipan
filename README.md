# 六爻排盘

[![CI](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/ci.yml/badge.svg)](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/ci.yml)
[![CodeQL](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/codeql.yml/badge.svg)](https://github.com/DemonAngela/liuyao_paipan/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于 FastAPI 与原生 HTML/CSS/JavaScript 的本地六爻起卦、排盘和辞典应用，把六爻传统规则编码为可检查、可测试、可复现的软件。

> **状态：持续维护、pre-1.0。** 项目用于学习、研究与可复现的规则讨论，不宣称是传统术数的唯一权威解释，也不应用于医疗、法律、金融等高风险决策。

## 功能

- 自动三枚铜钱起卦
- 手动逐爻、直接指定六爻和梅花时间起卦
- 本卦、变卦、纳甲、六亲、世应、空亡及项目展示用生克关系
- 按卦名查询卦辞、爻辞
- 查询今日或自定义日期时间的干支、公历和农历
- 同源提供前端页面和 API

## 规则边界

- 干支历使用 `lunar-python` 的节气换月结果；日柱采用 `sect=2`，即民用
  子初换日口径。
- 梅花时间起卦使用农历月、日及年支、时支序数。
- 三枚铜钱四种爻象的概率为 `1/8、3/8、3/8、1/8`。
- 生克、合冲等内容是本项目的展示筛选规则；六爻流派并无唯一统一口径，
  本项目不将其宣称为通行断卦标准。
- 时间起卦仍是实验性实现，不宣称已经实现有完整出处的传统年月日时起例。

## 环境

- Python 3.11 及以上，CI 使用 Python 3.13
- Windows 10/11 可使用项目启动脚本
- Node.js 仅用于开发时检查前端脚本语法

## 安装

```powershell
py -3.13 -m venv venv
.\venv\Scripts\python.exe -m pip install --require-hashes -r requirements.lock
```

开发环境安装测试和静态检查工具：

```powershell
.\venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.lock
```

`requirements*.lock` 固定全部传递依赖并校验哈希；修改
`requirements*.txt` 后，应使用其中固定的 `pip-tools` 重新生成锁文件。

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

版本发布会生成 GHCR 镜像；Release workflow 同时生成容器 SBOM、provenance
与针对镜像 digest 的 GitHub artifact attestation。

## 启动与停止

Windows 双击或执行：

```powershell
& '.\liuyao_start&stop.bat'
```

该入口会启动服务并在就绪后打开页面；启动 CMD 会持续保留，关闭该窗口即
关闭服务。需要后台管理时，也可分别执行：

```powershell
.\start.bat
.\stop.bat
```

服务默认只监听 `127.0.0.1:8000`，页面地址为
<http://127.0.0.1:8000/>。高级控制：

```powershell
.\scripts\server.ps1 start -Port 8765 -OpenBrowser
.\scripts\server.ps1 status
.\scripts\server.ps1 stop
```

开发时可为启动命令添加 `-Reload`。脚本会校验 PID 与进程启动时间，避免
停止 PID 被复用后的无关进程；运行状态和日志位于忽略提交的 `runtime/`。

也可直接运行：

```powershell
.\venv\Scripts\python.exe -m backend.main
```

可用环境变量：

| 变量 | 默认值 | 说明 |
|---|---:|---|
| `LIUYAO_HOST` | `127.0.0.1` | 监听地址 |
| `LIUYAO_PORT` | `8000` | 监听端口 |
| `LIUYAO_RELOAD` | `false` | 是否启用开发热重载 |
| `LIUYAO_CORS_ORIGINS` | 空 | 逗号分隔的跨域来源白名单 |

CORS 默认关闭并采用同源访问；白名单禁止 `*`。若需局域网访问，应显式
配置监听地址、防火墙和可信来源，不要把开发热重载用于生产环境。

## API

| 方法 | 路径 | 用途 |
|---|---|---|
| `POST` | `/api/qigua/auto` | 自动铜钱起卦 |
| `POST` | `/api/qigua/manual_step` | 生成一次手摇结果 |
| `POST` | `/api/qigua/manual_complete` | 提交六次手摇结果 |
| `POST` | `/api/qigua/specify` | 指定六爻及可选时间 |
| `POST` | `/api/qigua/time` | 梅花时间起卦 |
| `POST` | `/api/paipan/` | 排盘 |
| `GET` | `/api/ganzhi/today` | 查询今日干支、公历和农历 |
| `POST` | `/api/ganzhi/query` | 查询自定义时间的四柱干支、公历和农历 |
| `GET` | `/api/guaci/name/{gua_name}` | 按卦名查卦辞 |
| `GET` | `/api/yaoci/name/{gua_name}/{yao_pos}` | 按卦名和爻位查爻辞 |
| `GET` | `/healthz` | 服务存活检查 |

交互式 API 文档位于 `/docs`。输入模型使用严格类型和日期范围校验，无效
请求返回稳定的 `4xx`，服务端异常不会向客户端泄露内部细节。

## 干支历法基准

生产代码固定使用 `lunar_python==1.4.8` 作为可复现的软件基准。年柱与月柱
使用该基准计算的真实节气交接时刻；项目明确采用晚子时 `23:00-23:59`
不提前换日的 `sect=2` 约定。规则来源与验证范围见
[`docs/VALIDATION.md`](docs/VALIDATION.md) 与
[`docs/SOURCES_AND_SCOPE.md`](docs/SOURCES_AND_SCOPE.md)。

## 开发与验收

```powershell
.\venv\Scripts\python.exe -m ruff check backend tests init_project.py
.\venv\Scripts\python.exe -m compileall -q backend init_project.py
Get-ChildItem .\frontend\js\*.js | ForEach-Object { node --check $_.FullName }
.\venv\Scripts\python.exe -m pytest
```

重新生成六十四卦纳甲数据：

```powershell
.\venv\Scripts\python.exe -m backend.data.generate_64gua_table
```

生成器采用原子替换并固定写入 `backend/data/64gua_full.json`。架构和数据
边界见 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)，原始审查及修复状态
见 [`CODE_REVIEW.md`](CODE_REVIEW.md)。

Pull Request 还会运行多版本 Python 测试、安装后公共 API 检查、Docker
镜像构建与 CodeQL 安全分析。

## 发布

向远程推送 `v*` 标签会触发发布工作流；工作流先重复完整验收，再创建带
SHA-256 校验文件的源码压缩包、GHCR 容器镜像与构建证明，并创建
GitHub Release。发布版本应与 `backend/main.py` 中的应用版本一致。

## 维护与贡献

- [`CONTRIBUTING.md`](CONTRIBUTING.md) — 贡献与测试要求
- [`MAINTAINERS.md`](MAINTAINERS.md) — 维护职责与决策规则
- [`ROADMAP.md`](ROADMAP.md) — 可靠性与互操作路线图
- [`CHANGELOG.md`](CHANGELOG.md) — 兼容性/安全变更
- [`SECURITY.md`](SECURITY.md) — 漏洞报告方式
- [`docs/RELEASING.md`](docs/RELEASING.md) — 可重复发布流程
- [`docs/VALIDATION.md`](docs/VALIDATION.md) — 回归与基准验证策略

## License

[MIT License](LICENSE)
