"""
自动点击服务
"""

import time
from loguru import logger

try:
    import pyautogui
except ImportError:
    pyautogui = None


class AutoClickError(Exception):
    """自动点击错误"""
    pass


class AutoClickService:
    """自动点击服务"""
    
    def __init__(self):
        """初始化自动点击服务"""
        if pyautogui is None:
            raise AutoClickError("pyautogui未安装，请先安装: pip install pyautogui")
        
        # 设置pyautogui安全参数
        pyautogui.FAILSAFE = True  # 鼠标移到屏幕角落可中断
        pyautogui.PAUSE = 0.1      # 每次操作后暂停0.1秒
        
        logger.info("自动点击服务初始化完成")
    
    def click_position(self, x: int, y: int, delay_after: float = 0.5):
        """点击指定坐标
        
        Args:
            x: 点击位置x坐标
            y: 点击位置y坐标
            delay_after: 点击后等待时间（秒）
        """
        try:
            pyautogui.click(x, y)
            logger.info(f"点击坐标: ({x}, {y})")
            time.sleep(delay_after)
        except Exception as e:
            logger.error(f"点击失败: {e}")
            raise AutoClickError(f"点击失败: {e}")
    
    def move_and_click(self, x: int, y: int, duration: float = 0.3):
        """平滑移动鼠标并点击
        
        Args:
            x: 目标位置x坐标
            y: 目标位置y坐标
            duration: 移动持续时间（秒）
        """
        try:
            # 平滑移动鼠标
            pyautogui.moveTo(x, y, duration=duration)
            # 点击
            pyautogui.click()
            logger.info(f"移动并点击坐标: ({x}, {y})")
        except Exception as e:
            logger.error(f"移动并点击失败: {e}")
            raise AutoClickError(f"移动并点击失败: {e}")
