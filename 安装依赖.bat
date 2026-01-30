@echo off
chcp 65001 >nul
echo ========================================
echo 自动答题系统 - 安装依赖
echo ========================================
echo.
echo 正在安装Python依赖...
pip install -r requirements.txt
echo.
echo ========================================
echo 依赖安装完成！
echo ========================================
echo.
echo 注意：还需要安装Tesseract-OCR
echo 请访问：https://github.com/UB-Mannheim/tesseract/wiki
echo 或查看 README_AUTO_ANSWER.md 了解详细安装步骤
echo.
pause
