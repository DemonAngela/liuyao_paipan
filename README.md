# 六爻排盘

基于 FastAPI 与原生 HTML/CSS/JavaScript 的本地六爻起卦、排盘和辞典应用。

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

## 发布

向远程推送 `v*` 标签会触发发布工作流；工作流先重复完整验收，再创建带
SHA-256 校验文件的源码压缩包和 GitHub Release。发布版本应与
`backend/main.py` 中的应用版本一致。
