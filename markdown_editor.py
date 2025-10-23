#!/usr/bin/env python3
"""
K-Vault Rich Markdown Editor
Live preview with toolbar + formatting
"""
import re
from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QComboBox, QLabel, QToolBar, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QKeySequence
import markdown_it
from mdit_py_plugins import highlight, deflist, footnote
from pygments import highlight as pygments_highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class MarkdownEditor(QWidget):
    """Rich Markdown editor with live preview"""
    content_changed = pyqtSignal(str)
    note_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.preview_timer = QTimer()
        self.setup_markdown_parser()
        self.setup_ui()
        self.connect_signals()
    
    def setup_markdown_parser(self):
        """Setup advanced Markdown parser"""
        self.md = markdown_it.MarkdownIt('commonmark')
        self.md.use(highlight)
        self.md.use(deflist)
        self.md.use(footnote)
        
        # Custom link rendering for [[Note Title]]
        self.link_pattern = re.compile(r'\[\[([^\]\|]+)\]\]')
    
    def setup_ui(self):
        """Split editor + preview layout"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Editor side
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(12, 12, 12, 12)
        editor_layout.setSpacing(8)
        
        # Toolbar
        self.toolbar = self.create_toolbar()
        editor_layout.addWidget(self.toolbar)
        
        # Editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("SF Mono", 13))
        self.editor.setPlaceholderText(
            "# Rich Markdown Editor 🎉\n\n"
            "**Features:**\n"
            "- Live preview (bottom pane)\n"
            "- Bold *italic* formatting\n"
            "- H1-H6 headings\n"
            "- Code blocks (```python)\n"
            "- [[Wiki links]] to other notes\n"
            "- Tables | Lists | Quotes\n\n"
            "Start typing! 👇"
        )
        self.editor.setMinimumHeight(400)
        editor_layout.addWidget(self.editor, 1)
        
        layout.addWidget(editor_container, 1)
        
        # Preview side (splitter style)
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(12, 12, 12, 12)
        
        preview_label = QLabel("📖 Live Preview")
        preview_label.setFont(QFont("SF Pro", 11, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label)
        
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont("SF Pro", 13))
        self.preview.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 16px;
            }
        """)
        preview_layout.addWidget(self.preview, 1)
        
        layout.addWidget(preview_container, 1)
        
        # Update preview on start
        self.preview_timer.start(500)  # 500ms debounce
    
    def create_toolbar(self):
        """Rich editor toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        
        # Heading selector
        toolbar.addWidget(QLabel("Heading:"))
        self.heading_combo = QComboBox()
        self.heading_combo.addItems(["P", "H1", "H2", "H3", "H4", "H5", "H6"])
        self.heading_combo.currentTextChanged.connect(self.apply_heading)
        toolbar.addWidget(self.heading_combo)
        
        toolbar.addSeparator()
        
        # Bold
        bold_btn = QPushButton("𝐁")
        bold_btn.clicked.connect(lambda: self.toggle_format("bold"))
        toolbar.addWidget(bold_btn)
        
        # Italic
        italic_btn = QPushButton("𝐈")
        italic_btn.clicked.connect(lambda: self.toggle_format("italic"))
        toolbar.addWidget(italic_btn)
        
        toolbar.addSeparator()
        
        # Code
        code_btn = QPushButton("```")
        code_btn.clicked.connect(self.insert_code_block)
        toolbar.addWidget(code_btn)
        
        # Link
        link_btn = QPushButton("🔗")
        link_btn.clicked.connect(self.insert_wiki_link)
        toolbar.addWidget(link_btn)
        
        toolbar.addSeparator()
        
        # Actions
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_note)
        toolbar.addWidget(save_btn)
        
        return toolbar
    
    def connect_signals(self):
        """Connect editor signals"""
        self.editor.textChanged.connect(self.schedule_preview_update)
        self.preview_timer.timeout.connect(self.update_preview)
    
    def set_content(self, content: str):
        """Load note content"""
        self.editor.setText(content)
        self.update_preview()
    
    def get_content(self) -> str:
        """Get raw markdown content"""
        return self.editor.toPlainText()
    
    def schedule_preview_update(self):
        """Debounced preview update"""
        self.preview_timer.start(500)
    
    def update_preview(self):
        """Render live HTML preview"""
        markdown = self.get_content()
        
        # Convert wiki links to clickable
        html = markdown
        html = self.link_pattern.sub(r'<a href="#" class="wiki-link">\1</a>', html)
        
        # Render markdown
        try:
            html = self.md.render(markdown)
            # Basic CSS for preview
            css = """
            <style>
                body { font-family: -apple-system, SF Pro, sans-serif; line-height: 1.6; color: #1f2937; }
                h1 { font-size: 2em; font-weight: 700; margin: 1.5em 0 0.5em 0; }
                h2 { font-size: 1.5em; font-weight: 600; margin: 1.2em 0 0.4em 0; }
                h3 { font-size: 1.25em; font-weight: 600; margin: 1em 0 0.3em 0; }
                code { background: #f3f4f6; padding: 0.2em 0.4em; border-radius: 4px; font-family: 'SF Mono', monospace; }
                pre { background: #1f2937; color: #f9fafb; padding: 1em; border-radius: 6px; overflow-x: auto; }
                .wiki-link { color: #3b82f6; text-decoration: none; font-weight: 500; }
                .wiki-link:hover { text-decoration: underline; }
                blockquote { border-left: 4px solid #e5e7eb; padding-left: 1em; margin: 1em 0; color: #6b7280; }
                table { border-collapse: collapse; width: 100%; margin: 1em 0; }
                th, td { border: 1px solid #d1d5db; padding: 0.75em; text-align: left; }
                th { background: #f9fafb; font-weight: 600; }
            </style>
            """
            html = css + html
        except:
            html = f"<p><em>Preview error - {len(markdown)} chars</em></p>"
        
        self.preview.setHtml(html)
        self.content_changed.emit(markdown)
    
    # ===== FORMATTING =====
    def toggle_format(self, format_type: str):
        """Toggle bold/italic"""
        cursor = self.editor.textCursor()
        if format_type == "bold":
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Bold if cursor.charFormat().fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal)
            cursor.mergeCharFormat(fmt)
        elif format_type == "italic":
            fmt = QTextCharFormat()
            fmt.setFontItalic(not cursor.charFormat().fontItalic())
            cursor.mergeCharFormat(fmt)
        self.editor.setTextCursor(cursor)
    
    def apply_heading(self, level: str):
        """Apply heading"""
        if level == "P":
            return
        
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            heading = f"#{ ' #' * (int(level[1]) - 1) } {selected_text.strip()}\n\n"
            cursor.removeSelectedText()
            cursor.insertText(heading)
        else:
            cursor.insertText(f"#{ ' #' * (int(level[1]) - 1) } \n\n")
        
        self.editor.setTextCursor(cursor)
    
    def insert_code_block(self):
        """Insert code block"""
        cursor = self.editor.textCursor()
        cursor.insertText("```\n\n```\n")
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        self.editor.setTextCursor(cursor)
    
    def insert_wiki_link(self):
        """Insert [[Note Title]] wiki link"""
        cursor = self.editor.textCursor()
        cursor.insertText("[[Note Title]]")
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 11)
        self.editor.setTextCursor(cursor)
    
    def save_note(self):
        """Manual save"""
        self.note_saved.emit()
