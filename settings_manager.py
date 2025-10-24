#!/usr/bin/env python3
"""
K-Vault Settings Manager (Simple JSON)
"""
import json
import os
from typing import Dict, Any

class SettingsManager:
    """Simple persistent settings"""
    
    DEFAULTS = {
        "theme": "light",
        "font_size": 13,
        "auto_save_interval": 2000,
        "word_wrap": True
    }
    
    def __init__(self):
        self.settings_path = os.path.expanduser("~/.kvault/settings.json")
        self.settings = self.DEFAULTS.copy()
        self.load()
    
    def load(self):
        """Load from JSON"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
        except Exception:
            pass
    
    def save(self):
        """Save to JSON"""
        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass
    
    def get(self, key: str, default=None):
        return self.settings.get(key, default or self.DEFAULTS.get(key))
    
    def set(self, key: str, value):
        self.settings[key] = value
        self.save()
