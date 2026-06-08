#!/bin/bash

# 香港出入境数据统计系统启动脚本

echo "=========================================="
echo "香港出入境数据统计系统"
echo "=========================================="
echo ""

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "Python版本:"
python3 --version
echo ""

# 检查是否已安装依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "检测到缺少依赖，正在安装..."
    pip3 install -r requirements.txt
    echo ""
fi

# 检查数据库是否已初始化
if [ ! -f "database/border_stats.db" ]; then
    echo "数据库未初始化，开始初始化系统..."
    python3 init_system.py
    echo ""
fi

# 启动Flask应用
echo "启动Web服务器..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py
