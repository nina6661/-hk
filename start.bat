@echo off
chcp 65001 >nul
echo ==========================================
echo 香港出入境数据统计系统
echo ==========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo Python版本:
python --version
echo.

REM 检查依赖
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 检测到缺少依赖，正在安装...
    pip install -r requirements.txt
    echo.
)

REM 检查数据库
if not exist "database\border_stats.db" (
    echo 数据库未初始化，开始初始化系统...
    python init_system.py
    echo.
)

REM 启动应用
echo 启动Web服务器...
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务
echo.

python app.py
pause
