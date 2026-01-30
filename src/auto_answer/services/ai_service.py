"""
AI答题服务
"""

import re
import asyncio
import aiohttp
import io
from PIL import Image
from loguru import logger


class AIServiceError(Exception):
    """AI服务错误"""
    pass


class AIAnswerService:
    """AI答题服务"""
    
    def __init__(self, base_url: str = "http://localhost:8000", use_image: bool = True):
        """初始化AI答题服务
        
        Args:
            base_url: DoubaoFreeApi服务地址
            use_image: 是否使用图片识别（True=发送图片，False=发送文字）
        """
        self.base_url = base_url
        self.use_image = use_image
        self.timeout = aiohttp.ClientTimeout(total=30)  # 图片识别需要更长时间
        self.conversation_id = None  # 保存对话ID，复用同一个对话
        self.section_id = None  # 保存section_id
        logger.info(f"AI答题服务初始化完成，服务地址: {base_url}, 图片模式: {use_image}")
    
    def reset_conversation(self):
        """重置对话ID，开始新对话"""
        self.conversation_id = None
        self.section_id = None
        logger.info("已重置对话ID，将创建新对话")
    
    async def upload_image(self, image: Image.Image) -> dict:
        """上传图片到豆包服务器
        
        Args:
            image: PIL Image对象
            
        Returns:
            图片附件信息
        """
        try:
            # 将图片转换为字节
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # 上传图片
            url = f"{self.base_url}/api/file/upload"
            params = {
                "file_type": 1,  # 图片类型
                "file_name": "question.png"
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, params=params, data=img_byte_arr, headers={'Content-Type': 'application/octet-stream'}) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("图片上传成功")
                        return data
                    else:
                        error_text = await response.text()
                        raise AIServiceError(f"图片上传失败，状态码: {response.status}, 错误: {error_text}")
        
        except Exception as e:
            logger.error(f"图片上传失败: {e}")
            raise AIServiceError(f"图片上传失败: {e}")
    
    def parse_answer(self, response_text: str) -> str:
        """从AI响应中解析答案选项
        
        Args:
            response_text: AI返回的完整文本
            
        Returns:
            答案选项（A/B/C/D）
        """
        # 使用正则表达式提取答案选项
        # 优先匹配单独的选项字母
        match = re.search(r'\b([ABCD])\b', response_text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        
        # 如果没找到，尝试匹配任何A/B/C/D
        match = re.search(r'[ABCD]', response_text, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        
        logger.warning(f"无法从响应中解析答案: {response_text}")
        raise AIServiceError("无法解析AI返回的答案")
    
    async def get_answer(self, question: str = None, image: Image.Image = None, retry: int = 3, use_deep_think: bool = False) -> str:
        """获取题目答案
        
        Args:
            question: 题目文字（文字模式使用）
            image: 题目图片（图片模式使用）
            retry: 失败重试次数
            use_deep_think: 是否使用深度思考
            
        Returns:
            答案字符串（如"A"、"B"等）
            
        Raises:
            AIServiceError: API调用失败时抛出
        """
        if self.use_image:
            # 图片模式：直接发送图片
            if image is None:
                raise AIServiceError("图片模式下必须提供图片")
            
            # 上传图片
            attachment = await self.upload_image(image)
            
            # 构造请求payload
            payload = {
                "prompt": "请识别图片中的选择题，并直接回答选项字母（A/B/C/D），只需要回答字母，不要解释。",
                "guest": False,  # 使用登录模式（session.json中的配置）
                "conversation_id": self.conversation_id,  # 复用同一个对话
                "section_id": self.section_id,
                "attachments": [attachment],
                "use_deep_think": use_deep_think
            }
        else:
            # 文字模式：发送OCR识别的文字
            if not question or not question.strip():
                raise AIServiceError("文字模式下题目文字为空")
            
            payload = {
                "prompt": f"请回答以下选择题，只需要回答选项字母（A/B/C/D）：\n{question}",
                "guest": False,  # 使用登录模式（session.json中的配置）
                "conversation_id": self.conversation_id,  # 复用同一个对话
                "section_id": self.section_id,
                "use_deep_think": use_deep_think
            }
        
        url = f"{self.base_url}/api/chat/completions"
        
        # 实现指数退避重试
        for attempt in range(retry + 1):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            answer_text = data.get("text", "")
                            
                            # 保存conversation_id和section_id，用于下次请求
                            if data.get("conversation_id"):
                                self.conversation_id = data.get("conversation_id")
                            if data.get("section_id"):
                                self.section_id = data.get("section_id")
                            
                            if not answer_text:
                                raise AIServiceError("AI返回空响应")
                            
                            # 解析答案
                            answer = self.parse_answer(answer_text)
                            logger.info(f"AI答题成功，答案: {answer}")
                            return answer
                        else:
                            error_text = await response.text()
                            raise AIServiceError(f"API请求失败，状态码: {response.status}, 错误: {error_text}")
            
            except AIServiceError:
                raise
            except Exception as e:
                if attempt < retry:
                    # 指数退避：1秒、2秒、4秒
                    wait_time = 2 ** attempt
                    logger.warning(f"AI请求失败 (尝试 {attempt + 1}/{retry + 1}): {e}，{wait_time}秒后重试")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"AI请求失败，已达最大重试次数: {e}")
                    raise AIServiceError(f"AI请求失败: {e}")
