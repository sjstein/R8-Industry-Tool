from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os
import sys
from datetime import datetime


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Run8 Industry Tool")
        self.setFixedSize(500, 250)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(12)  # spacing between icon and text

        # Left side - Icon
        icon_label = QLabel()
        icon_path = resource_path("app_icon.ico")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            # Scale to medium size (64x64)
            scaled_pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            icon_label.setText("🔧")
            icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        icon_label.setFixedWidth(64)  # Prevent icon from expanding horizontally
        main_layout.addWidget(icon_label)

        # Right side - Information
        info_layout = QVBoxLayout()

        # Program name
        name_label = QLabel("<h2>Run8 Industry Tool</h2>")
        name_label.setTextFormat(Qt.TextFormat.RichText)
        info_layout.addWidget(name_label)

        # Version and build date
        try:
            from version import VERSION, BUILD_DATE
        except ImportError:
            VERSION = "1.0.0"
            BUILD_DATE = "Unknown"

        version_label = QLabel(f"<b>Version:</b> {VERSION}")
        version_label.setTextFormat(Qt.TextFormat.RichText)
        info_layout.addWidget(version_label)

        build_date_label = QLabel(f"<b>Build Date:</b> {BUILD_DATE}")
        build_date_label.setTextFormat(Qt.TextFormat.RichText)
        info_layout.addWidget(build_date_label)

        # Spacer
        info_layout.addSpacing(10)

        # Author info
        author_label = QLabel("""
            <b>Author:</b> Josh Stein<br>
            <b>Contact:</b> Sinistar on the Depot forums<br>
            <br>
            <b>Found a bug? Request a feature?</b><br>
            Please add an issue to the repository: 
            <a href="https://github.com/sjstein/R8-Industry-Tool/issues">GitHub Issues</a>
        """)
        author_label.setTextFormat(Qt.TextFormat.RichText)
        author_label.setOpenExternalLinks(True)  # Enable clicking links to open in browser
        info_layout.addWidget(author_label)

        # Add stretch to push everything to the top
        info_layout.addStretch()

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setMaximumWidth(100)
        info_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(info_layout)
