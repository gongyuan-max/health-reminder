#!/usr/bin/env python3
"""
Health Reminder - 健康提醒助手
主应用入口
"""

import sys
import os
from pathlib import Path

# 添加源码目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow
from src.utils.config import Config
from src.utils.logger import setup_logger

# 设置日志
setup_logger()

def main():
    """应用主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("Health Reminder")
    app.setApplicationVersion("1.0.0")
    
    # 初始化配置
    Config.init_config()
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
