"""
配置数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Region:
    """屏幕区域"""
    x: int
    y: int
    width: int
    height: int


@dataclass
class Coordinate:
    """坐标点"""
    x: int
    y: int


@dataclass
class AnswerConfig:
    """答题配置"""
    question_area: Optional[Region] = None
    options: Dict[str, Coordinate] = field(default_factory=dict)
    next_button: Optional[Coordinate] = None
    
    def is_valid(self) -> bool:
        """检查配置是否完整"""
        return (
            self.question_area is not None and
            len(self.options) >= 2 and
            self.next_button is not None
        )
    
    def get_option_coordinate(self, option: str) -> Coordinate:
        """获取选项坐标
        
        Args:
            option: 选项字母（A/B/C/D）
            
        Returns:
            选项坐标
            
        Raises:
            ValueError: 如果选项未配置
        """
        if option not in self.options:
            raise ValueError(f"未配置选项 {option}")
        return self.options[option]
    
    def to_dict(self) -> dict:
        """转换为字典用于JSON序列化"""
        return {
            "question_area": {
                "x": self.question_area.x,
                "y": self.question_area.y,
                "width": self.question_area.width,
                "height": self.question_area.height
            } if self.question_area else None,
            "options": {
                k: {"x": v.x, "y": v.y} 
                for k, v in self.options.items()
            },
            "next_button": {
                "x": self.next_button.x,
                "y": self.next_button.y
            } if self.next_button else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AnswerConfig':
        """从字典创建配置对象"""
        question_area = None
        if data.get("question_area"):
            qa = data["question_area"]
            question_area = Region(qa["x"], qa["y"], qa["width"], qa["height"])
        
        options = {}
        if data.get("options"):
            options = {
                k: Coordinate(v["x"], v["y"])
                for k, v in data["options"].items()
            }
        
        next_button = None
        if data.get("next_button"):
            nb = data["next_button"]
            next_button = Coordinate(nb["x"], nb["y"])
        
        return cls(
            question_area=question_area,
            options=options,
            next_button=next_button
        )
