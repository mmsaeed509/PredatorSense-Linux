import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from app.ui.main_window import CustomShapeWindow

def main():
    # Performance optimizations for QApplication - set before creating app
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Disable animations for better performance
    app.setEffectEnabled(Qt.UI_AnimateMenu, False)
    app.setEffectEnabled(Qt.UI_AnimateCombo, False)
    app.setEffectEnabled(Qt.UI_AnimateTooltip, False)
    
    # Set application properties for better resource management
    app.setQuitOnLastWindowClosed(True)
    
    # Create and show window
    window = CustomShapeWindow()
    window.show()
    
    # Run application
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
