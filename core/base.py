"""
core/base.py - 术数方法抽象基类
定义统一的输入获取、计算、渲染接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DivinationMethod(ABC):
    """所有占卜方法的基类"""

    @abstractmethod
    def get_input_fields(self) -> List[Dict[str, Any]]:
        """
        返回该术数需要的输入字段列表，每个字段为一个字典：
        { 'name': str, 'label': str, 'type': str, 'default': Any, 'options': Optional[list] }
        type 可以是 'text', 'number', 'select', 'datetime' 等
        """
        pass

    @abstractmethod
    def compute(self, **kwargs) -> Dict[str, Any]:
        """
        执行排盘/起课计算，返回字典结果。
        kwargs 包含 get_input_fields 中定义的字段的值。
        """
        pass

    @abstractmethod
    def render(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        将计算结果转换为前端展示所需的数据结构（可选）。
        如果返回空字典，则直接使用 result 展示。
        """
        pass