"""
周易六爻排盘项目初始化脚本
运行后将自动生成完整的目录结构与空文件框架
"""

import os
import sys

def create_dir(path):
    """创建目录，若已存在则忽略"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"创建目录: {path}")
    else:
        print(f"目录已存在: {path}")

def create_file(filepath, content=""):
    """创建文件并写入可选内容，若已存在则询问是否覆盖"""
    if os.path.exists(filepath):
        response = input(f"文件已存在: {filepath}，是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print(f"跳过文件: {filepath}")
            return
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"创建文件: {filepath}")

def main():
    # 项目根目录（默认为当前工作目录）
    root = os.getcwd()
    print(f"项目根目录: {root}")

    # 1. 创建 backend 目录及其子目录
    backend = os.path.join(root, 'backend')
    create_dir(backend)

    api_dir = os.path.join(backend, 'api')
    create_dir(api_dir)

    core_dir = os.path.join(backend, 'core')
    create_dir(core_dir)

    models_dir = os.path.join(backend, 'models')
    create_dir(models_dir)

    data_dir = os.path.join(backend, 'data')
    create_dir(data_dir)

    utils_dir = os.path.join(backend, 'utils')
    create_dir(utils_dir)

    # 2. 创建 frontend 目录及其子目录
    frontend = os.path.join(root, 'frontend')
    create_dir(frontend)

    css_dir = os.path.join(frontend, 'css')
    create_dir(css_dir)

    js_dir = os.path.join(frontend, 'js')
    create_dir(js_dir)

    assets_dir = os.path.join(frontend, 'assets')
    create_dir(assets_dir)
    icons_dir = os.path.join(assets_dir, 'icons')
    create_dir(icons_dir)

    # 3. 创建 Python 包所需的 __init__.py 文件（使目录成为包）
    for sub in [backend, api_dir, core_dir, models_dir, utils_dir]:
        create_file(os.path.join(sub, '__init__.py'), '# 自动生成的包初始化文件\n')

    # 4. 创建后端模块文件（空骨架）
    # main.py
    create_file(os.path.join(backend, 'main.py'), '''"""
FastAPI 主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="周易六爻排盘API", version="1.0.0")

# 允许跨域（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "周易六爻排盘系统"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
''')

    # api/qigua.py
    create_file(os.path.join(api_dir, 'qigua.py'), '''"""
起卦相关 API 路由
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/qigua", tags=["起卦"])

@router.post("/auto")
async def auto_qigua():
    """电脑自动起卦"""
    pass

@router.post("/manual_step")
async def manual_step():
    """手动摇卦单步"""
    pass

@router.post("/manual_complete")
async def manual_complete():
    """手动摇卦完成"""
    pass

@router.post("/specify")
async def specify_qigua():
    """手工指定起卦"""
    pass

@router.post("/time")
async def time_qigua():
    """时间起卦"""
    pass
''')

    # api/paipan.py
    create_file(os.path.join(api_dir, 'paipan.py'), '''"""
排盘相关 API 路由
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/paipan", tags=["排盘"])

@router.post("/")
async def paipan():
    """核心排盘接口"""
    pass

@router.post("/relation")
async def relation():
    """单独计算生克冲合关系"""
    pass
''')

    # api/cidian.py
    create_file(os.path.join(api_dir, 'cidian.py'), '''"""
卦辞爻辞相关 API 路由
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["卦辞爻辞"])

@router.get("/guaci/{gua_id}")
async def get_guaci(gua_id: int):
    """获取指定卦的卦辞"""
    pass

@router.get("/yaoci/{gua_id}/{yao_pos}")
async def get_yaoci(gua_id: int, yao_pos: int):
    """获取指定爻的爻辞"""
    pass
''')

    # core/liuyao_engine.py
    create_file(os.path.join(core_dir, 'liuyao_engine.py'), '''"""
六爻排盘核心引擎
"""
class LiuyaoEngine:
    def __init__(self):
        pass
    
    def paipan(self, gua_data):
        """执行完整排盘流程"""
        pass
''')

    # core/ganzhi.py
    create_file(os.path.join(core_dir, 'ganzhi.py'), '''"""
干支历法计算模块
"""
def get_current_ganzhi():
    """获取当前年月日时的干支"""
    pass

def get_xunkong(day_ganzhi):
    """根据日干支计算旬空"""
    pass
''')

    # core/najia.py
    create_file(os.path.join(core_dir, 'najia.py'), '''"""
纳甲装卦模块
"""
def determine_gua_gong(ben_gua):
    """判定卦宫"""
    pass

def an_shiyao(gua):
    """安世应"""
    pass

def na_dizhi(gua):
    """纳地支"""
    pass
''')

    # core/liuqin.py
    create_file(os.path.join(core_dir, 'liuqin.py'), '''"""
六亲配置模块
"""
def assign_liuqin(gua, gong_wuxing):
    """为各爻配置六亲"""
    pass
''')

    # core/liushen.py
    create_file(os.path.join(core_dir, 'liushen.py'), '''"""
六神排布模块
"""
def assign_liushen(day_gan):
    """根据日干确定六神顺序"""
    pass
''')

    # core/xunkong.py
    create_file(os.path.join(core_dir, 'xunkong.py'), '''"""
旬空计算模块
"""
def mark_xunkong(yao_list, day_ganzhi):
    """标注旬空之爻"""
    pass
''')

    # core/shengke.py
    create_file(os.path.join(core_dir, 'shengke.py'), '''"""
生克冲合计算模块
"""
def calculate_relations(gua):
    """计算六合、六冲、三合、生旺墓绝"""
    pass
''')

    # core/guaci.py
    create_file(os.path.join(core_dir, 'guaci.py'), '''"""
卦辞爻辞管理模块
"""
import json
import os

class GuaciManager:
    def __init__(self, data_dir):
        self.guaci_file = os.path.join(data_dir, '64gua.json')
        self.yaoci_file = os.path.join(data_dir, 'yaoci.json')
    
    def load_guaci(self, gua_id):
        pass
    
    def load_yaoci(self, gua_id, yao_pos):
        pass
''')

    # models/gua.py
    create_file(os.path.join(models_dir, 'gua.py'), '''"""
卦象数据模型
"""
from pydantic import BaseModel
from typing import List, Optional

class YaoData(BaseModel):
    position: int
    yin_yang: int  # 0阴 1阳
    is_changing: bool
    dizhi: Optional[str] = None
    wuxing: Optional[str] = None
    liuqin: Optional[str] = None
    liushen: Optional[str] = None
    is_kong: bool = False

class GuaData(BaseModel):
    name: str
    yao_list: List[YaoData]
    shi_yao: int
    ying_yao: int
''')

    # models/request.py
    create_file(os.path.join(models_dir, 'request.py'), '''"""
请求数据模型
"""
from pydantic import BaseModel
from typing import List

class QiguaRequest(BaseModel):
    method: str  # auto, manual, specify, time
    yao_values: List[int] = []  # 手工指定时的阴阳值
''')

    # utils/validator.py
    create_file(os.path.join(utils_dir, 'validator.py'), '''"""
输入校验模块
"""
def validate_gua_input(data):
    pass
''')

    # utils/constants.py
    create_file(os.path.join(utils_dir, 'constants.py'), '''"""
常量定义（六合、六冲、三合、生旺墓绝表）
"""
# 六合
LIU_HE = {
    ('子', '丑'), ('寅', '亥'), ('卯', '戌'),
    ('辰', '酉'), ('巳', '申'), ('午', '未')
}

# 六冲
LIU_CHONG = {
    ('子', '午'), ('丑', '未'), ('寅', '申'),
    ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
}

# 三合局
SAN_HE = {
    '水': {'申', '子', '辰'},
    '火': {'寅', '午', '戌'},
    '金': {'巳', '酉', '丑'},
    '木': {'亥', '卯', '未'}
}

# 生旺墓绝表（五行对应）
SHENG_WANG_MU_JUE = {
    '金': {'生': '巳', '旺': '酉', '墓': '丑', '绝': '寅'},
    '木': {'生': '亥', '旺': '卯', '墓': '未', '绝': '申'},
    '火': {'生': '寅', '旺': '午', '墓': '戌', '绝': '亥'},
    '水': {'生': '申', '旺': '子', '墓': '辰', '绝': '巳'},
    '土': {'生': '申', '旺': '子', '墓': '辰', '绝': '巳'}
}

# 八纯卦纳甲表（内卦初爻，外卦四爻起始地支）
NAJIA_TABLE = {
    '乾': {'start': '子', 'outer_start': '午', 'order': '顺'},
    '坎': {'start': '寅', 'outer_start': '申', 'order': '顺'},
    '震': {'start': '子', 'outer_start': '午', 'order': '顺'},
    '艮': {'start': '辰', 'outer_start': '戌', 'order': '顺'},
    '坤': {'start': '未', 'outer_start': '丑', 'order': '逆'},
    '巽': {'start': '丑', 'outer_start': '未', 'order': '逆'},
    '离': {'start': '卯', 'outer_start': '酉', 'order': '逆'},
    '兑': {'start': '巳', 'outer_start': '亥', 'order': '逆'}
}
''')

    # 5. 创建数据文件（占位JSON）
    create_file(os.path.join(data_dir, '64gua.json'), '{\n  "1": {\n    "name": "乾为天",\n    "gua_ci": "元亨利贞。"\n  }\n}')
    create_file(os.path.join(data_dir, 'yaoci.json'), '{\n  "1": {\n    "1": "初九：潜龙勿用。",\n    "2": "九二：见龙在田，利见大人。"\n  }\n}')

    # 6. 创建前端文件
    create_file(os.path.join(frontend, 'index.html'), '''<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>周易六爻排盘系统</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <h1>周易六爻排盘 · 纳甲六爻在线排卦</h1>
    <div id="app">
        <!-- 起卦控制区 -->
        <div id="control-panel">
            <!-- 待实现 -->
        </div>
        <!-- 卦象展示区 -->
        <div id="gua-display">
            <!-- 待实现 -->
        </div>
        <!-- 卦辞区 -->
        <div id="guaci-area">
            <!-- 待实现 -->
        </div>
    </div>
    <script src="js/utils.js"></script>
    <script src="js/qigua.js"></script>
    <script src="js/paipan.js"></script>
</body>
</html>
''')

    create_file(os.path.join(css_dir, 'style.css'), '/* 样式表 - 待完善 */\nbody { font-family: "Microsoft YaHei", sans-serif; }')
    create_file(os.path.join(js_dir, 'utils.js'), '// 工具函数\n')
    create_file(os.path.join(js_dir, 'qigua.js'), '// 起卦交互逻辑\n')
    create_file(os.path.join(js_dir, 'paipan.js'), '// 排盘结果渲染\n')

    # 7. 创建 requirements.txt
    create_file(os.path.join(root, 'requirements.txt'), '''fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.3
# 可选：用于干支历法
# sxtwl
''')

    # 8. 创建 Windows 启动脚本 start.bat
    create_file(os.path.join(root, 'start.bat'), '''@echo off
chcp 65001 >nul
echo 正在启动周易六爻排盘系统...
cd /d %~dp0
call .\\venv\\Scripts\\activate.bat 2>nul || echo 虚拟环境未找到，请先创建虚拟环境并安装依赖
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
''')

    # 9. 创建 README.md
    create_file(os.path.join(root, 'README.md'), '''# 周易六爻排盘系统

基于《增删卜易》专家经验的六爻排盘工具。

## 快速开始

1. 创建虚拟环境：
python -m venv venv
venv\Scripts\activate
 
2. 安装依赖：
pip install -r requirements.txt
3. 运行后端服务：
uvicorn backend.main:app --reload
4. 打开浏览器访问 `http://127.0.0.1:8000` 或直接打开 `frontend/index.html`（需配置API地址）。

## 项目结构
详见架构设计文档。
''')


print("\n项目目录初始化完成！")
print("下一步：创建虚拟环境并安装依赖：")
print("  python -m venv venv")
print("  venv\\Scripts\\activate")
print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()