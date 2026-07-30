"""
卦象数据模型定义
用于 API 请求/响应序列化
"""

from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel


class BianguaYaoDataModel(BaseModel):
    """变爻数据模型（用于动爻的变爻详情）"""
    yin_yang: int
    dizhi: str
    wuxing: str
    liuqin: str
    is_kong: bool = False   # 新增：变爻是否旬空


class YaoDataModel(BaseModel):
    """爻数据模型"""
    position: int
    yin_yang: int
    is_changing: bool
    dizhi: str
    wuxing: str
    liuqin: str
    liushen: str
    is_kong: bool
    biangua_yao: Optional[BianguaYaoDataModel] = None   # 动爻的变爻详情
    biangua_info: Optional[BianguaYaoDataModel] = None  # 新增：变卦对应爻信息（无论是否动爻）
    shengke: str = ''
    fushen: Optional[str] = None   # 伏神，格式如“父母子水”，无则显示“—”
    # 新增日月冲合与暗动字段
    ri_chong: bool = False      # 日建冲
    yue_chong: bool = False     # 月建冲
    ri_he: bool = False         # 日建合
    yue_he: bool = False        # 月建合
    is_andong: bool = False     # 暗动
    is_ripo: bool = False       # 日破
    is_yuepo: bool = False      # 月破
    # 日建关系
    ri_zhi: bool = False      # 临日（值日）
    ri_sheng: bool = False    # 日生
    ri_ke: bool = False       # 日克
    ri_chong: bool = False    # 日冲
    ri_he: bool = False       # 日合
    # 月建关系
    yue_zhi: bool = False
    yue_sheng: bool = False
    yue_ke: bool = False
    yue_chong: bool = False
    yue_he: bool = False
    # 日月关系补充
    ri_lin: bool = False       # 日建五行相同（临/扶）
    yue_lin: bool = False      # 月建五行相同


class GuaDataModel(BaseModel):
    """完整排盘结果模型"""
    ben_gua_name: str
    bian_gua_name: str
    yao_list: List[YaoDataModel]
    shi_yao: int
    ying_yao: int
    gan_zhi: Dict[str, str]
    xunkong: Tuple[str, str]
    relations: Dict[str, Any]
    special_attr: Optional[str] = None   # 新增：六冲/六合/归魂/游魂
    bian_special_attr: Optional[str] = None  # 新增：变卦特殊标记


class QiguaRequest(BaseModel):
    """起卦请求模型"""
    method: str
    yao_values: Optional[List[int]] = None
    changing_yao: Optional[List[bool]] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = 0


class QiguaResponse(BaseModel):
    """起卦响应模型"""
    yao_list: List[int]
    changing_yao: List[bool]
    timestamp: Dict[str, int]

relations = {
    "liuhe": [...],
    "liuchong": [...],
    "sanhe": [...],  # 包含成局的详细信息
    "banhe": [...],  # 半合局
    "dongyao_chonghe": [...],
    "shengwangmujue": [...],
    "andong_list": [1, 3],  # 暗动爻位
    "ripo_list": [2],  # 日破爻位
    "yuepo_list": [4]  # 月破爻位
}