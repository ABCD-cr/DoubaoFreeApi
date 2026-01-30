"""
屏幕截图服务
"""

from PIL import Image, ImageGrab
from loguru import logger


class ScreenCaptureError(Exception):
    """屏幕截图错误"""
    pass


class ScreenCaptureService:
    """屏幕截图服务"""
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        """截取指定区域的屏幕
        
        Args:
            x: 区域左上角x坐标
            y: 区域左上角y坐标
            width: 区域宽度
            height: 区域高度
            
        Returns:
            PIL Image对象
            
        Raises:
            ScreenCaptureError: 截图失败时抛出
        """
        try:
            # bbox格式：(left, upper, right, lower)
            bbox = (x, y, x + width, y + height)
            image = ImageGrab.grab(bbox=bbox)
            
            if image is None:
                raise ScreenCaptureError("截图返回空对象")
            
            logger.info(f"成功截取屏幕区域: ({x}, {y}, {width}, {height})")
            return image
            
        except Exception as e:
            logger.error(f"屏幕截图失败: {e}")
            raise ScreenCaptureError(f"屏幕截图失败: {e}")
