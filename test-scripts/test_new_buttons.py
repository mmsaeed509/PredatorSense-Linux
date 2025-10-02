#!/usr/bin/env python3
"""
Test script to verify the new ModeButtonWithLabel design
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from app.utils.ui_utils import ModeButtonWithLabel

def main():
    # Set attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Create test window
    window = QWidget()
    window.setWindowTitle("Mode Button Test")
    window.setStyleSheet("background-color: #0a0a0a;")
    window.resize(400, 200)
    
    # Create layout with buttons
    layout = QHBoxLayout(window)
    layout.setSpacing(20)
    
    # Create buttons
    auto_btn = ModeButtonWithLabel("Auto")
    max_btn = ModeButtonWithLabel("Max")
    custom_btn = ModeButtonWithLabel("Custom")
    
    # Set one as checked for testing
    auto_btn.setChecked(True)
    
    layout.addWidget(auto_btn)
    layout.addWidget(max_btn)
    layout.addWidget(custom_btn)
    
    window.show()
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())