"""
请求数据模型
"""
from pydantic import BaseModel
from typing import List

class QiguaRequest(BaseModel):
    method: str  # auto, manual, specify, time
    yao_values: List[int] = []  # 手工指定时的阴阳值
