"""
自动答题系统启动入口
"""

import asyncio
import sys
import os
import subprocess
import time
from tkinter import messagebox
from loguru import logger

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.auto_answer.gui.main_window import MainWindow
from src.auto_answer.gui.region_selector import RegionSelector
from src.auto_answer.gui.option_configurator import OptionConfigurator
from src.auto_answer.core.config_manager import ConfigManager
from src.auto_answer.core.controller import AnswerController


class AutoAnswerApp:
    """自动答题应用"""
    
    def __init__(self):
        """初始化应用"""
        # 配置日志
        logger.add(
            "logs/auto_answer_{time}.log",
            rotation="1 day",
            retention="7 days",
            level="INFO"
        )
        
        # API服务进程
        self.api_process = None
        
        # 初始化配置管理器
        self.config_manager = ConfigManager("auto_answer_config.json")
        
        try:
            self.config_manager.load_config()
        except Exception as e:
            logger.warning(f"加载配置失败: {e}")
        
        # 初始化GUI
        self.window = MainWindow()
        
        # 设置回调
        self.window.on_start_api_callback = self.on_start_api
        self.window.on_stop_api_callback = self.on_stop_api
        self.window.on_select_question_area_callback = self.on_select_question_area
        self.window.on_configure_options_callback = self.on_configure_options
        self.window.on_start_answering_callback = self.on_start_answering
        self.window.on_stop_answering_callback = self.on_stop_answering
        
        # 初始化控制器
        gui_callbacks = {
            "update_status": self.window.update_status,
            "update_progress": self.window.update_progress,
            "append_log": self.window.append_log,
            "on_answering_complete": self.on_answering_complete
        }
        self.controller = AnswerController(
            self.config_manager, 
            gui_callbacks,
            use_image_mode=True  # 使用图片模式，直接发图片给豆包
        )
        
        logger.info("自动答题应用初始化完成（图片模式）")
    
    def on_start_api(self):
        """启动API服务"""
        try:
            self.window.append_log("正在检查豆包API服务...")
            
            # 先检查API服务是否已经在运行
            try:
                import requests
                response = requests.get("http://localhost:8000/docs", timeout=2)
                if response.status_code == 200:
                    self.window.set_api_buttons_state(running=True)
                    self.window.append_log("✓ 豆包API服务已在运行")
                    logger.info("豆包API服务已在运行")
                    return
            except:
                pass  # API服务未运行，继续启动
            
            self.window.append_log("正在启动豆包API服务...")
            
            # 启动API服务进程
            self.api_process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(__file__)
            )
            
            # 等待服务启动
            time.sleep(3)
            
            # 检查进程是否还在运行
            if self.api_process.poll() is None:
                self.window.set_api_buttons_state(running=True)
                self.window.append_log("✓ 豆包API服务已启动")
                logger.info("豆包API服务已启动")
            else:
                raise Exception("API服务启动失败")
                
        except Exception as e:
            self.window.append_log(f"✗ API服务启动失败: {e}")
            messagebox.showerror("错误", f"API服务启动失败: {e}")
            logger.error(f"API服务启动失败: {e}")
    
    def on_stop_api(self):
        """停止API服务"""
        try:
            if self.api_process:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                self.api_process = None
                
            self.window.set_api_buttons_state(running=False)
            self.window.append_log("✓ 豆包API服务已停止")
            logger.info("豆包API服务已停止")
            
        except Exception as e:
            self.window.append_log(f"✗ API服务停止失败: {e}")
            logger.error(f"API服务停止失败: {e}")
    
    def on_select_question_area(self):
        """选择题目区域"""
        def callback(x, y, width, height):
            self.config_manager.set_question_area(x, y, width, height)
            self.window.append_log(f"题目区域已设置: ({x}, {y}, {width}, {height})")
            messagebox.showinfo("成功", "题目区域已设置")
        
        selector = RegionSelector(callback)
        selector.start_selection()
    
    def on_configure_options(self):
        """配置答案选项"""
        def on_complete():
            self.window.append_log("所有选项配置完成")
        
        configurator = OptionConfigurator(self.config_manager, on_complete)
        configurator.start_configuration()
    
    def on_start_answering(self):
        """开始答题"""
        # 检查API服务是否运行（通过实际请求检测）
        try:
            import requests
            response = requests.get("http://localhost:8000/docs", timeout=2)
            if response.status_code != 200:
                messagebox.showerror("错误", "请先启动豆包API服务")
                return
        except:
            messagebox.showerror("错误", "请先启动豆包API服务")
            return
        
        # 检查配置
        config = self.config_manager.get_config()
        if not config.is_valid():
            messagebox.showerror("错误", "配置不完整，请先完成配置")
            return
        
        # 获取题目总数
        total_questions = self.window.get_total_questions()
        if total_questions <= 0:
            return
        
        # 获取是否使用深度思考
        use_deep_think = self.window.get_use_deep_think()
        
        # 更新按钮状态
        self.window.set_buttons_state(answering=True)
        
        # 启动答题流程
        asyncio.run(self.controller.start_answering(total_questions, use_deep_think))
    
    def on_stop_answering(self):
        """停止答题"""
        self.controller.stop_answering()
        self.window.set_buttons_state(answering=False)
    
    def on_answering_complete(self):
        """答题完成"""
        self.window.set_buttons_state(answering=False)
        messagebox.showinfo("完成", "答题已完成！")
    
    def run(self):
        """运行应用"""
        self.window.append_log("欢迎使用自动答题系统")
        self.window.append_log("1. 先点击'启动API服务'")
        self.window.append_log("2. 然后配置题目区域和答案选项")
        self.window.append_log("3. 最后点击'开始答题'")
        self.window.run()
        
        # 程序退出时清理
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
            except:
                pass


def main():
    """主函数"""
    try:
        app = AutoAnswerApp()
        app.run()
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        messagebox.showerror("错误", f"应用启动失败: {e}")


if __name__ == "__main__":
    main()
