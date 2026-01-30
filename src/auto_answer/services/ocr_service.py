"""
OCR识别服务
"""

from PIL import Image, ImageEnhance, ImageFilter
from loguru import logger

try:
    import pytesseract
except ImportError:
    pytesseract = None


class OCRError(Exception):
    """OCR识别错误"""
    pass


class OCRService:
    """OCR识别服务"""
    
    def __init__(self, lang: str = 'chi_sim+eng'):
        """初始化OCR服务
        
        Args:
            lang: Tesseract语言包，默认支持简体中文和英文
        """
        if pytesseract is None:
            raise OCRError("pytesseract未安装，请先安装: pip install pytesseract")
        
        self.lang = lang
        logger.info(f"OCR服务初始化完成，语言: {lang}")
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """图像预处理以提高OCR准确率
        
        Args:
            image: 原始图像
            
        Returns:
            预处理后的图像
        """
        # 转换为灰度图
        image = image.convert('L')
        
        # 增强对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # 二值化处理
        threshold = 128
        image = image.point(lambda x: 0 if x < threshold else 255, '1')
        
        return image
    
    def extract_text(self, image: Image.Image) -> str:
        """从图像中提取文字
        
        Args:
            image: PIL Image对象
            
        Returns:
            识别出的文字字符串
            
        Raises:
            OCRError: OCR识别失败时抛出
        """
        try:
            # 预处理图像
            processed_image = self.preprocess_image(image)
            
            # OCR识别
            # --psm 6: 假设单个文本块
            config = '--psm 6'
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.lang,
                config=config
            )
            
            # 清理文本
            text = text.strip()
            
            if not text:
                logger.warning("OCR识别结果为空")
                raise OCRError("未识别到题目文字")
            
            logger.info(f"OCR识别成功，文字长度: {len(text)}")
            return text
            
        except OCRError:
            raise
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            raise OCRError(f"OCR识别失败: {e}")
