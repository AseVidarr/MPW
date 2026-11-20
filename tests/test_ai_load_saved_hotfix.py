import ast
from pathlib import Path

source = Path(__file__).resolve().parents[1] / 'source' / 'workstation.py'
text = source.read_text(encoding='utf-8')
tree = ast.parse(text)
assert 'def load_saved_ai_prompt(self):' in text
assert 'self.ai_versions.itemDoubleClicked.connect' in text
assert 'self.ai_load_saved.clicked.connect(self.load_saved_ai_prompt)' in text
assert 'Qt.ItemDataRole.UserRole, vid' in text
assert 'self.set_ai_editor_values(style, lyrics)' in text
print('OK: Prompt laden Hotfix – Syntax und UI-Anbindung')
