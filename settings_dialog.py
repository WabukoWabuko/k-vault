#!/usr/bin/env python3
"""
K-Vault Settings Dialog (Simple)
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, 
                             QSpinBox, QCheckBox, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt
from settings_manager import SettingsManager

class SettingsDialog(QDialog):
    def __init__(self, settings: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.resize(400, 300)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Theme
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        theme_layout.addRow("Theme:", self.theme_combo)
        layout.addWidget(theme_group)
        
        # Editor
        editor_group = QGroupBox("Editor")
        editor_layout = QFormLayout(editor_group)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 24)
        editor_layout.addRow("Font Size:", self.font_size_spin)
        self.auto_save_spin = QSpinBox()
        self.auto_save_spin.setRange(500, 10000)
        self.auto_save_spin.setSuffix("ms")
        editor_layout.addRow("Auto-save:", self.auto_save_spin)
        self.word_wrap_check = QCheckBox("Word Wrap")
        editor_layout.addRow(self.word_wrap_check)
        layout.addWidget(editor_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def load_settings(self):
        theme = self.settings.get("theme")
        self.theme_combo.setCurrentText(theme.capitalize())
        self.font_size_spin.setValue(self.settings.get("font_size"))
        self.auto_save_spin.setValue(self.settings.get("auto_save_interval"))
        self.word_wrap_check.setChecked(self.settings.get("word_wrap"))
    
    def save_settings(self):
        self.settings.set("theme", self.theme_combo.currentText().lower())
        self.settings.set("font_size", self.font_size_spin.value())
        self.settings.set("auto_save_interval", self.auto_save_spin.value())
        self.settings.set("word_wrap", self.word_wrap_check.isChecked())
        self.accept()
