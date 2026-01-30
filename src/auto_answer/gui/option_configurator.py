"""
选项配置器
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable
from loguru import logger

from .region_selector import RegionSelector


class OptionConfigurator:
    """选项配置器"""
    
    def __init__(self, config_manager, on_complete: Callable):
        """初始化选项配置器
        
        Args:
            config_manager: 配置管理器
            on_complete: 配置完成回调
        """
        self.config_manager = config_manager
        self.on_complete = on_complete
        self.options_to_configure = ['A', 'B', 'C', 'D', '下一题']
        self.current_index = 0
        
    def start_configuration(self):
        """开始配置流程"""
        self.current_index = 0
        self._configure_next_option()
    
    def _configure_next_option(self):
        """配置下一个选项"""
        if self.current_index >= len(self.options_to_configure):
            # 所有选项配置完成
            messagebox.showinfo("完成", "所有选项配置完成！")
            if self.on_complete:
                self.on_complete()
            return
        
        option = self.options_to_configure[self.current_index]
        
        # 显示提示
        messagebox.showinfo(
            "配置选项",
            f"请点击屏幕上的 '{option}' 选项位置"
        )
        
        # 创建区域选择器（用于点击位置）
        selector = RegionSelector(self._on_option_selected)
        selector.start_selection()
    
    def _on_option_selected(self, x: int, y: int, width: int, height: int):
        """选项位置选择完成
        
        Args:
            x: 区域左上角x坐标
            y: 区域左上角y坐标
            width: 区域宽度
            height: 区域高度
        """
        # 计算中心点
        center_x = x + width // 2
        center_y = y + height // 2
        
        option = self.options_to_configure[self.current_index]
        
        if option == '下一题':
            # 配置下一题按钮
            self.config_manager.set_next_button(center_x, center_y)
            logger.info(f"配置下一题按钮: ({center_x}, {center_y})")
        else:
            # 配置答案选项
            self.config_manager.set_option_coordinate(option, center_x, center_y)
            logger.info(f"配置选项 {option}: ({center_x}, {center_y})")
        
        # 继续配置下一个选项
        self.current_index += 1
        self._configure_next_option()
