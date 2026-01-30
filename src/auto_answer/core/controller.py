"""
答题控制器
"""

import asyncio
from typing import Callable, Dict
from loguru import logger

from ..services.screen_capture import ScreenCaptureService, ScreenCaptureError
from ..services.ocr_service import OCRService, OCRError
from ..services.ai_service import AIAnswerService, AIServiceError
from ..services.auto_click import AutoClickService, AutoClickError
from .config_manager import ConfigManager


class AnswerController:
    """答题控制器"""
    
    def __init__(self, config_manager: ConfigManager, gui_callbacks: Dict[str, Callable], use_image_mode: bool = True):
        """初始化答题控制器
        
        Args:
            config_manager: 配置管理器实例
            gui_callbacks: GUI回调函数字典
            use_image_mode: 是否使用图片模式（True=发图片，False=OCR文字）
        """
        self.config_manager = config_manager
        self.gui_callbacks = gui_callbacks
        self.use_image_mode = use_image_mode
        
        # 初始化服务
        self.screen_capture = ScreenCaptureService()
        self.ai_service = AIAnswerService(use_image=use_image_mode)
        self.auto_click = AutoClickService()
        
        # 只在文字模式下初始化OCR服务
        if not use_image_mode:
            self.ocr_service = OCRService()
        else:
            self.ocr_service = None
        
        # 状态
        self.is_running = False
        self.current_question = 0
        
        mode_text = "图片模式" if use_image_mode else "文字模式"
        logger.info(f"答题控制器初始化完成，使用{mode_text}")
    
    def update_status(self, status: str):
        """更新状态"""
        if "update_status" in self.gui_callbacks:
            self.gui_callbacks["update_status"](status)
    
    def update_progress(self, current: int, total: int):
        """更新进度"""
        if "update_progress" in self.gui_callbacks:
            self.gui_callbacks["update_progress"](current, total)
    
    def append_log(self, message: str):
        """添加日志"""
        if "append_log" in self.gui_callbacks:
            self.gui_callbacks["append_log"](message)
    
    async def answer_one_question(self, question_num: int, use_deep_think: bool = False) -> bool:
        """回答一道题目
        
        Args:
            question_num: 当前题号
            use_deep_think: 是否使用深度思考
            
        Returns:
            是否成功完成
        """
        try:
            config = self.config_manager.get_config()
            
            if not config.is_valid():
                self.append_log("错误: 配置不完整，请先完成配置")
                return False
            
            # 1. 截图
            self.update_status("正在截图...")
            self.append_log(f"题目 {question_num}: 开始截图")
            
            image = self.screen_capture.capture_region(
                config.question_area.x,
                config.question_area.y,
                config.question_area.width,
                config.question_area.height
            )
            
            # 2. 根据模式处理
            if self.use_image_mode:
                # 图片模式：直接发送图片给AI
                status_text = "正在发送图片给AI..."
                if use_deep_think:
                    status_text += "（深度思考模式）"
                self.update_status(status_text)
                self.append_log(f"题目 {question_num}: 正在发送图片给AI识别{'（深度思考）' if use_deep_think else ''}")
                
                answer = await self.ai_service.get_answer(image=image, use_deep_think=use_deep_think)
                self.append_log(f"题目 {question_num}: AI答案 - {answer}")
            else:
                # 文字模式：先OCR识别，再发送文字
                self.update_status("正在识别题目...")
                self.append_log(f"题目 {question_num}: 正在识别文字")
                
                question_text = self.ocr_service.extract_text(image)
                self.append_log(f"题目 {question_num}: 识别结果 - {question_text[:50]}...")
                
                status_text = "正在请求AI答题..."
                if use_deep_think:
                    status_text += "（深度思考模式）"
                self.update_status(status_text)
                self.append_log(f"题目 {question_num}: 正在请求AI{'（深度思考）' if use_deep_think else ''}")
                
                answer = await self.ai_service.get_answer(question=question_text, use_deep_think=use_deep_think)
                self.append_log(f"题目 {question_num}: AI答案 - {answer}")
            
            # 3. 点击答案
            self.update_status(f"正在点击答案 {answer}...")
            self.append_log(f"题目 {question_num}: 正在点击答案 {answer}")
            
            option_coord = config.get_option_coordinate(answer)
            self.auto_click.move_and_click(option_coord.x, option_coord.y)
            
            # 4. 等待500ms
            await asyncio.sleep(0.5)
            
            # 5. 点击下一题
            self.update_status("正在点击下一题...")
            self.append_log(f"题目 {question_num}: 正在点击下一题")
            
            self.auto_click.move_and_click(
                config.next_button.x,
                config.next_button.y
            )
            
            # 6. 等待5秒加载下一题（避免频率限制）
            self.append_log(f"题目 {question_num}: 等待5秒避免频率限制...")
            await asyncio.sleep(5.0)
            
            self.append_log(f"题目 {question_num}: 完成")
            return True
            
        except OCRError as e:
            self.append_log(f"题目 {question_num}: OCR识别失败 - {e}")
            logger.warning(f"OCR识别失败，跳过题目 {question_num}: {e}")
            # 点击下一题继续
            try:
                config = self.config_manager.get_config()
                self.auto_click.move_and_click(
                    config.next_button.x,
                    config.next_button.y
                )
                await asyncio.sleep(1.0)
            except:
                pass
            return False
            
        except AIServiceError as e:
            error_msg = str(e)
            self.append_log(f"题目 {question_num}: AI请求失败 - {e}")
            logger.warning(f"AI请求失败，跳过题目 {question_num}: {e}")
            
            # 检测是否是频率限制错误
            if "rate limited" in error_msg or "710022004" in error_msg:
                self.append_log(f"检测到频率限制，重置对话并等待10秒后继续...")
                logger.warning(f"检测到频率限制，重置对话并等待10秒")
                # 重置对话ID，下次请求会创建新对话
                self.ai_service.reset_conversation()
                await asyncio.sleep(10.0)
            
            # 点击下一题继续
            try:
                config = self.config_manager.get_config()
                self.auto_click.move_and_click(
                    config.next_button.x,
                    config.next_button.y
                )
                await asyncio.sleep(1.0)
            except:
                pass
            return False
            
        except ValueError as e:
            self.append_log(f"题目 {question_num}: 答案映射失败 - {e}")
            logger.warning(f"答案映射失败，跳过题目 {question_num}: {e}")
            # 点击下一题继续
            try:
                config = self.config_manager.get_config()
                self.auto_click.move_and_click(
                    config.next_button.x,
                    config.next_button.y
                )
                await asyncio.sleep(1.0)
            except:
                pass
            return False
            
        except Exception as e:
            self.append_log(f"题目 {question_num}: 未知错误 - {e}")
            logger.error(f"答题过程发生错误: {e}")
            return False
    
    async def start_answering(self, total_questions: int, use_deep_think: bool = False):
        """开始答题流程
        
        Args:
            total_questions: 题目总数
            use_deep_think: 是否使用深度思考
        """
        self.is_running = True
        self.current_question = 0
        
        mode_text = "（深度思考模式）" if use_deep_think else ""
        self.append_log(f"开始答题，共 {total_questions} 题{mode_text}")
        self.update_status("答题中...")
        
        for i in range(1, total_questions + 1):
            if not self.is_running:
                self.append_log("答题已停止")
                break
            
            self.current_question = i
            self.update_progress(i, total_questions)
            
            success = await self.answer_one_question(i, use_deep_think)
            
            # 检查是否达到最后一题
            if i == total_questions:
                self.append_log("所有题目已完成！")
                self.update_status("完成")
                break
        
        self.is_running = False
        
        if "on_answering_complete" in self.gui_callbacks:
            self.gui_callbacks["on_answering_complete"]()
    
    def stop_answering(self):
        """停止答题流程"""
        self.is_running = False
        self.update_status("已停止")
        self.append_log("用户停止答题")
        logger.info("答题流程已停止")
