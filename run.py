#!/usr/bin/env python3
"""启动脚本"""
from app import app

if __name__ == '__main__':
    print("\n" + "="*60)
    print("香港出入境数据统计系统")
    print("="*60)
    print("访问地址: http://localhost:5002")
    print("数据范围: 2021-01-01 至 2026-05-20")
    print("="*60)
    print("按 Ctrl+C 停止服务器\n")
    
    app.run(host='0.0.0.0', port=5002, debug=False)
