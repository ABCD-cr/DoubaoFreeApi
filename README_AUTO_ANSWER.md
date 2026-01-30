# 自动答题系统使用文档

## 简介

自动答题系统是基于DoubaoFreeApi的扩展功能，可以自动识别屏幕上的题目，调用豆包AI获取答案，并自动点击选项完成答题。

## 功能特点

- 🖼️ 屏幕区域选择：框选题目显示区域
- 🔍 OCR文字识别：自动识别题目内容
- 🤖 AI智能答题：调用豆包AI获取答案
- 🖱️ 自动点击：自动点击答案选项和下一题按钮
- ⏹️ 智能停止：最后一题答完后自动停止

## 安装步骤

### 1. 安装Python依赖

```bash
cd DoubaoFreeApi
pip install -r requirements.txt
```

### 2. 安装Tesseract-OCR

Tesseract-OCR是开源的OCR识别引擎，需要单独安装。

#### Windows系统

1. 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
2. 运行安装程序，记住安装路径（如：`C:\Program Files\Tesseract-OCR`）
3. 将安装路径添加到系统环境变量PATH中

或者使用命令行安装：
```bash
# 使用Chocolatey
choco install tesseract

# 使用Scoop
scoop install tesseract
```

#### macOS系统

```bash
brew install tesseract
brew install tesseract-lang  # 安装中文语言包
```

#### Linux系统

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 简体中文语言包

# CentOS/RHEL
sudo yum install tesseract
```

### 3. 验证安装

```bash
tesseract --version
```

如果显示版本信息，说明安装成功。

## 使用步骤

### 1. 启动豆包API服务

首先需要启动DoubaoFreeApi服务：

```bash
cd DoubaoFreeApi
python app.py
```

服务将在 `http://localhost:8000` 运行。

### 2. 启动自动答题系统

在新的终端窗口中：

```bash
cd DoubaoFreeApi
python auto_answer_main.py
```

### 3. 配置系统

#### 3.1 选择题目区域

1. 点击"选择题目区域"按钮
2. 屏幕会显示半透明覆盖层
3. 用鼠标框选题目显示的区域
4. 释放鼠标完成选择
5. 按ESC键可以取消选择

#### 3.2 配置答案选项

1. 点击"配置答案选项"按钮
2. 系统会依次提示配置A、B、C、D选项和"下一题"按钮
3. 对于每个选项，用鼠标框选该选项在屏幕上的位置
4. 系统会自动计算中心点作为点击位置

### 4. 开始答题

1. 在"题目总数"输入框中输入题目数量
2. 点击"开始答题"按钮
3. 系统会自动执行以下流程：
   - 截取题目区域
   - OCR识别题目文字
   - 调用豆包AI获取答案
   - 点击对应的答案选项
   - 点击"下一题"按钮
   - 重复以上步骤直到完成所有题目

### 5. 停止答题

如需中途停止，点击"停止答题"按钮。

## 配置文件

系统会自动保存配置到 `auto_answer_config.json` 文件，下次启动时会自动加载。

配置文件格式：
```json
{
  "question_area": {
    "x": 100,
    "y": 200,
    "width": 800,
    "height": 600
  },
  "options": {
    "A": {"x": 150, "y": 400},
    "B": {"x": 150, "y": 450},
    "C": {"x": 150, "y": 500},
    "D": {"x": 150, "y": 550}
  },
  "next_button": {
    "x": 400,
    "y": 650
  }
}
```

## 日志文件

系统会自动记录日志到 `logs/` 目录，日志文件按天轮转，保留7天。

## 常见问题

### 1. OCR识别不准确

**解决方法：**
- 确保题目区域选择准确，不要包含多余内容
- 题目文字要清晰，避免模糊或重叠
- 可以调整屏幕分辨率或缩放比例
- 确保安装了中文语言包（chi_sim）

### 2. 点击位置不准确

**解决方法：**
- 重新配置答案选项，确保框选的区域准确
- 系统会自动计算中心点，确保选项按钮在框选区域内
- 注意高DPI屏幕可能需要调整坐标

### 3. AI返回的答案无法识别

**解决方法：**
- 检查题目是否为选择题（A/B/C/D格式）
- 确保豆包API服务正常运行
- 查看日志了解AI返回的具体内容

### 4. pytesseract找不到tesseract命令

**解决方法：**

在代码中指定tesseract路径（Windows）：
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

或者将tesseract添加到系统PATH环境变量。

### 5. pyautogui安全机制触发

**解决方法：**
- pyautogui有FAILSAFE机制，将鼠标移到屏幕左上角可以中断程序
- 这是安全特性，防止程序失控
- 如需继续，重新启动程序即可

## 注意事项

1. **使用前测试**：建议先用少量题目测试，确保配置正确
2. **保持屏幕稳定**：答题过程中不要移动或调整答题界面
3. **网络连接**：确保能够访问豆包API服务
4. **题目格式**：目前仅支持A/B/C/D格式的选择题
5. **答题速度**：系统会在每次操作后等待，确保页面加载完成

## 技术支持

如遇到问题，请查看：
1. 日志文件：`logs/auto_answer_*.log`
2. GUI界面的日志显示区域
3. 控制台输出信息

## 许可证

本项目遵循MIT许可证。
