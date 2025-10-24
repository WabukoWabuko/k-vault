#!/usr/bin/env python3
"""
K-Vault Theme Manager (Manual QSS - Python 3.12 Compatible)
Light/Dark/Auto theme switching without external libs
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from settings_manager import SettingsManager
import sys
import os

class ThemeManager(QObject):
    """Handles manual QSS theme application"""
    theme_changed = pyqtSignal(str)
    
    LIGHT_QSS = """
    QMainWindow {
        background: #ffffff;
        color: #1f2937;
    }
    QTreeWidget {
        background: #ffffff;
        color: #1f2937;
        border: 1px solid #e5e7eb;
        font-family: 'SF Pro', -apple-system, sans-serif;
        font-size: 13px;
    }
    QTreeWidget::item {
        padding: 6px 12px;
        border-bottom: 1px solid #f3f4f6;
    }
    QTreeWidget::item:selected {
        background: #3b82f6;
        color: white;
    }
    QTextEdit {
        background: #ffffff;
        color: #1f2937;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 12px;
        font-family: 'SF Mono', monospace;
        font-size: 13px;
    }
    QLineEdit {
        background: #ffffff;
        color: #1f2937;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 8px;
        font-size: 13px;
    }
    QLineEdit:focus {
        border: 2px solid #3b82f6;
    }
    QPushButton {
        background: #f9fafb;
        color: #374151;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }
    QPushButton:hover {
        background: #f3f4f6;
    }
    QPushButton:pressed {
        background: #e5e7eb;
    }
    QStatusBar {
        background: #f9fafb;
        color: #6b7280;
        border-top: 1px solid #e5e7eb;
        padding: 4px 8px;
        font-size: 12px;
    }
    QToolBar {
        background: #f8fafc;
        border: none;
        spacing: 4px;
        padding: 4px;
    }
    QSplitter::handle {
        background: #e5e7eb;
        width: 4px;
    }
    """
    
    DARK_QSS = """
    QMainWindow {
        background: #0f172a;
        color: #f1f5f9;
    }
    QTreeWidget {
        background: #1e293b;
        color: #f1f5f9;
        border: 1px solid #334155;
        font-family: 'SF Pro', -apple-system, sans-serif;
        font-size: 13px;
    }
    QTreeWidget::item {
        padding: 6px 12px;
        border-bottom: 1px solid #334155;
    }
    QTreeWidget::item:selected {
        background: #1e40af;
        color: #ffffff;
    }
    QTextEdit {
        background: #1e293b;
        color: #f1f5f9;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 12px;
        font-family: 'SF Mono', monospace;
        font-size: 13px;
    }
    QLineEdit {
        background: #1e293b;
        color: #f1f5f9;
        border: 1px solid #475569;
        border-radius: 6px;
        padding: 8px;
        font-size: 13px;
    }
    QLineEdit:focus {
        border: 2px solid #60a5fa;
    }
    QPushButton {
        background: #334155;
        color: #f1f5f9;
        border: 1px solid #475569;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }
    QPushButton:hover {
        background: #475569;
    }
    QPushButton:pressed {
        background: #4b5563;
    }
    QStatusBar {
        background: #1e293b;
        color: #94a3b8;
        border-top: 1px solid #334155;
        padding: 4px 8px;
        font-size: 12px;
    }
    QToolBar {
        background: #1e293b;
        border: none;
        spacing: 4px;
        padding: 4px;
    }
    QSplitter::handle {
        background: #334155;
        width: 4px;
    }
    """
    
    def __init__(self, settings: SettingsManager):
        super().__init__()
        self.settings = settings
        self.current_theme = "light"
    
    def apply_theme(self, app: QApplication):
        """Apply current theme using QSS"""
        theme = self.settings.get("theme", "light")
        
        if theme == "dark":
            app.setStyleSheet(self.DARK_QSS)
        else:
            app.setStyleSheet(self.LIGHT_QSS)
        
        self.current_theme = theme
        self.theme_changed.emit(theme)
    
    def toggle_theme(self):
        """Toggle between light/dark"""
        current = self.settings.get("theme", "light")
        new_theme = "dark" if current == "light" else "light"
        self.settings.set("theme", new_theme)
        self.apply_theme(QApplication.instance())
