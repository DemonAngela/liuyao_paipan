"""兼容旧导入路径的起卦请求模型导出。"""

from .gua import QiguaRequest, SpecifyQiguaRequest, TimeQiguaRequest

__all__ = [
    "QiguaRequest",
    "SpecifyQiguaRequest",
    "TimeQiguaRequest",
]
