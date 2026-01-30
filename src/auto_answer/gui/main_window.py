"""
主窗口GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional, Callable
from loguru import logger


class MainWindow:
    """主窗口"""
    
    def __init__(self):
        """初始化主窗口"""
        self.root = tk.Tk()
        self.root.title("自动答题系统")
        self.root.geometry("600x500")
        
        # 回调函数
        self.on_start_api_callback: Optional[Callable] = None
        self.on_stop_api_callback: Optional[Callable] = None
        self.on_select_question_area_callback: Optional[Callable] = None
        self.on_configure_options_callback: Optional[Callable] = None
        self.on_start_answering_callback: Optional[Callable] = None
        self.on_stop_answering_callback: Optional[Callable] = None
        
        # UI组件
        self.total_questions_var = tk.StringVar(value="10")
        self.progress_var = tk.StringVar(value="0/0")
        self.status_var = tk.StringVar(value="就绪")
        self.api_status_var = tk.StringVar(value="API: 未启动")
        self.use_deep_think_var = tk.BooleanVar(value=False)
        
        self.start_button: Optional[tk.Button] = None
        self.stop_button: Optional[tk.Button] = None
        self.log_text: Optional[scrolledtext.ScrolledText] = None
        self.start_api_button: Optional[tk.Button] = None
        self.stop_api_button: Optional[tk.Button] = None
        
        self.create_widgets()
        
        logger.info("主窗口初始化完成")
    
    def create_widgets(self):
        """创建所有UI组件"""
        # 标题
        title_label = tk.Label(
            self.root,
            text="自动答题系统",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # API服务控制区域
        api_frame = ttk.LabelFrame(self.root, text="豆包API服务", padding=10)
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # API状态显示
        ttk.Label(
            api_frame,
            textvariable=self.api_status_var,
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=5)
        
        # API控制按钮
        self.start_api_button = ttk.Button(
            api_frame,
            text="启动API服务",
            command=self.on_start_api
        )
        self.start_api_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.stop_api_button = ttk.Button(
            api_frame,
            text="停止API服务",
            command=self.on_stop_api,
            state=tk.DISABLED
        )
        self.stop_api_button.grid(row=1, column=1, padx=5, pady=5)
        
        # 配置区域
        config_frame = ttk.LabelFrame(self.root, text="答题配置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 题目总数
        ttk.Label(config_frame, text="题目总数:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(
            config_frame,
            textvariable=self.total_questions_var,
            width=10
        ).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 深度思考选项
        ttk.Checkbutton(
            config_frame,
            text="启用深度思考（更准确但更慢）",
            variable=self.use_deep_think_var
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 选择题目区域按钮
        ttk.Button(
            config_frame,
            text="选择题目区域",
            command=self.on_select_question_area
        ).grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # 配置答案选项按钮
        ttk.Button(
            config_frame,
            text="配置答案选项",
            command=self.on_configure_options
        ).grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # 控制区域
        control_frame = ttk.LabelFrame(self.root, text="控制", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 开始答题按钮
        self.start_button = ttk.Button(
            control_frame,
            text="开始答题",
            command=self.on_start_answering
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 停止答题按钮
        self.stop_button = ttk.Button(
            control_frame,
            text="停止答题",
            command=self.on_stop_answering,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 状态区域
        status_frame = ttk.LabelFrame(self.root, text="状态", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 进度显示
        ttk.Label(status_frame, text="进度:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(
            status_frame,
            textvariable=self.progress_var,
            font=("Arial", 10, "bold")
        ).grid(row=0, column=1, sticky=tk.W)
        
        # 状态显示
        ttk.Label(status_frame, text="状态:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(
            status_frame,
            textvariable=self.status_var
        ).grid(row=1, column=1, sticky=tk.W)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.root, text="日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def on_start_api(self):
        """处理"启动API服务"按钮点击"""
        logger.info("点击启动API服务按钮")
        if self.on_start_api_callback:
            self.on_start_api_callback()
    
    def on_stop_api(self):
        """处理"停止API服务"按钮点击"""
        logger.info("点击停止API服务按钮")
        if self.on_stop_api_callback:
            self.on_stop_api_callback()
    
    def on_select_question_area(self):
        """处理"选择题目区域"按钮点击"""
        logger.info("点击选择题目区域按钮")
        if self.on_select_question_area_callback:
            self.on_select_question_area_callback()
    
    def on_configure_options(self):
        """处理"配置答案选项"按钮点击"""
        logger.info("点击配置答案选项按钮")
        if self.on_configure_options_callback:
            self.on_configure_options_callback()
    
    def on_start_answering(self):
        """处理"开始答题"按钮点击"""
        logger.info("点击开始答题按钮")
        if self.on_start_answering_callback:
            self.on_start_answering_callback()
    
    def on_stop_answering(self):
        """处理"停止答题"按钮点击"""
        logger.info("点击停止答题按钮")
        if self.on_stop_answering_callback:
            self.on_stop_answering_callback()
    
    def update_progress(self, current: int, total: int):
        """更新进度显示"""
        self.progress_var.set(f"{current}/{total}")
    
    def update_status(self, status: str):
        """更新状态文本"""
        self.status_var.set(status)
    
    def append_log(self, message: str):
        """添加日志消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def set_api_buttons_state(self, running: bool):
        """设置API按钮状态
        
        Args:
            running: API是否正在运行
        """
        if running:
            self.start_api_button.config(state=tk.DISABLED)
            self.stop_api_button.config(state=tk.NORMAL)
            self.api_status_var.set("API: 运行中 ✓")
        else:
            self.start_api_button.config(state=tk.NORMAL)
            self.stop_api_button.config(state=tk.DISABLED)
            self.api_status_var.set("API: 未启动")
    
    def set_buttons_state(self, answering: bool):
        """设置按钮状态
        
        Args:
            answering: 是否正在答题
        """
        if answering:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def get_total_questions(self) -> int:
        """获取题目总数"""
        try:
            return int(self.total_questions_var.get())
        except ValueError:
            messagebox.showerror("错误", "题目总数必须是数字")
            return 0
    
    def get_use_deep_think(self) -> bool:
        """获取是否使用深度思考"""
        return self.use_deep_think_var.get()
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()
