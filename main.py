"""
Entry point - Chạy: python main.py
Yêu cầu: pip install pygame
"""
import sys, os

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(__file__))

from ui.app import SokobanApp

if __name__ == '__main__':
    app = SokobanApp()
    app.run()