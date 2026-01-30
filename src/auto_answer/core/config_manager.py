"""
配置管理器
"""

import json
import os
from pathlib import Path
from typing import Optional
from loguru import logger

from ..models.config import AnswerConfig, Region, Coordinate


class ConfigError(Exception):
    """配置错误"""
    pass


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "auto_answer_config.json"):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config: Optional[AnswerConfig] = None
        
    def load_config(self) -> AnswerConfig:
        """加载配置文件
        
        Returns:
            配置对象
        """
        if not os.path.exists(self.config_file):
            logger.warning(f"配置文件不存在: {self.config_file}，使用默认配置")
            self.config = AnswerConfig()
            return self.config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.config = AnswerConfig.from_dict(data)
            logger.info(f"成功加载配置文件: {self.config_file}")
            return self.config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise ConfigError(f"加载配置文件失败: {e}")
    
    def save_config(self, config: Optional[AnswerConfig] = None):
        """保存配置到文件
        
        Args:
            config: 配置对象，如果为None则保存当前配置
        """
        if config is None:
            config = self.config
        
        if config is None:
            raise ConfigError("没有可保存的配置")
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"成功保存配置文件: {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise ConfigError(f"保存配置文件失败: {e}")
    
    def set_question_area(self, x: int, y: int, width: int, height: int):
        """设置题目区域
        
        Args:
            x: 区域左上角x坐标
            y: 区域左上角y坐标
            width: 区域宽度
            height: 区域高度
        """
        if self.config is None:
            self.config = AnswerConfig()
        
        self.config.question_area = Region(x, y, width, height)
        self.save_config()
        logger.info(f"设置题目区域: ({x}, {y}, {width}, {height})")
    
    def set_option_coordinate(self, option: str, x: int, y: int):
        """设置答案选项坐标
        
        Args:
            option: 选项字母（A/B/C/D）
            x: x坐标
            y: y坐标
        """
        if self.config is None:
            self.config = AnswerConfig()
        
        self.config.options[option] = Coordinate(x, y)
        self.save_config()
        logger.info(f"设置选项 {option} 坐标: ({x}, {y})")
    
    def set_next_button(self, x: int, y: int):
        """设置"下一题"按钮坐标
        
        Args:
            x: x坐标
            y: y坐标
        """
        if self.config is None:
            self.config = AnswerConfig()
        
        self.config.next_button = Coordinate(x, y)
        self.save_config()
        logger.info(f"设置下一题按钮坐标: ({x}, {y})")
    
    def get_config(self) -> AnswerConfig:
        """获取当前配置
        
        Returns:
            配置对象
        """
        if self.config is None:
            self.load_config()
        return self.config
