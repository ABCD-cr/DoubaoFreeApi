"""
区域选择器
"""

import tkinter as tk
from typing import Callable, Optional, Tuple
from loguru import logger


class RegionSelector:
    """屏幕区域选择器"""
    
    def __init__(self, callback: Callable[[int, int, int, int], None]):
        """初始化区域选择器
        
        Args:
            callback: 选择完成后的回调函数，接收(x, y, width, height)
        """
        self.callback = callback
        self.overlay_window: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self.start_x: Optional[int] = None
        self.start_y: Optional[int] = None
        self.rect_id: Optional[int] = None
        
    def start_selection(self):
        """启动区域选择，显示全屏半透明覆盖层"""
        # 创建根窗口（如果不存在）
        root = tk.Tk()
        root.withdraw()  # 隐藏根窗口
        
        # 创建全屏顶层窗口
        self.overlay_window = tk.Toplevel(root)
        self.overlay_window.attributes('-fullscreen', True)
        self.overlay_window.attributes('-alpha', 0.3)  # 半透明
        self.overlay_window.attributes('-topmost', True)  # 置顶
        
        # 创建Canvas用于绘制选择框
        self.canvas = tk.Canvas(
            self.overlay_window,
            cursor='cross',
            bg='gray',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_move)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # 绑定ESC键取消选择
        self.overlay_window.bind('<Escape>', lambda e: self.cancel_selection())
        
        logger.info("区域选择器已启动")
        
    def on_mouse_down(self, event):
        """处理鼠标按下事件"""
        self.start_x = event.x
        self.start_y = event.y
        
        # 如果已有选择框，删除它
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        # 创建新的选择框
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red',
            width=2
        )
    
    def on_mouse_move(self, event):
        """处理鼠标移动事件，实时更新选择框"""
        if self.start_x is not None and self.start_y is not None:
            # 更新选择框
            self.canvas.coords(
                self.rect_id,
                self.start_x, self.start_y,
                event.x, event.y
            )
    
    def on_mouse_up(self, event):
        """处理鼠标释放事件，完成选择"""
        if self.start_x is None or self.start_y is None:
            return
        
        end_x = event.x
        end_y = event.y
        
        # 计算区域坐标（确保左上角为起点）
        x = min(self.start_x, end_x)
        y = min(self.start_y, end_y)
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)
        
        logger.info(f"区域选择完成: ({x}, {y}, {width}, {height})")
        
        # 关闭覆盖层
        self.overlay_window.destroy()
        
        # 调用回调函数
        if self.callback:
            self.callback(x, y, width, height)
    
    def cancel_selection(self):
        """取消选择，关闭覆盖层"""
        logger.info("区域选择已取消")
        if self.overlay_window:
            self.overlay_window.destroy()
