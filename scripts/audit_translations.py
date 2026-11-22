#!/usr/bin/env python3
"""Read-only static translation coverage audit for MPW."""
import ast, collections, pathlib
p=pathlib.Path(__file__).resolve().parent.parent/'source'/'workstation.py'
tree=ast.parse(p.read_text(encoding='utf-8'))
assignments={}
for node in ast.walk(tree):
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        targets=node.targets if isinstance(node,ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target,ast.Name) and target.id.startswith('UI_'):
                try: assignments[target.id]=ast.literal_eval(node.value)
                except (ValueError,TypeError): pass
categories={'QPushButton':'UI_CONTROL_TRANSLATIONS','QLabel':'UI_FIELD_TRANSLATIONS','QCheckBox':'UI_FIELD_TRANSLATIONS','QGroupBox':'UI_SECTION_TRANSLATIONS'}
rows=[]
for constructor,table in categories.items():
    values=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id==constructor and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):
            values.add(node.args[0].value)
    translations=assignments.get(table,{})
    coverage={lang:sum(v in translations.get(lang,{}) for v in values) for lang in ('en','fr','es','it')}
    missing=sorted(v for v in values if v not in translations.get('en',{}))
    rows.append((constructor,table,values,coverage,missing))
print('# MPW v2.2.0 Alpha 15 – Statische Übersetzungsinventur')
print('\nQuelle: `source/workstation.py` aus Alpha 14. Analyse ohne Änderung an der Laufzeitlogik.')
print('\n| Element | Eindeutige statische Texte | EN | FR | ES | IT |')
print('|---|---:|---:|---:|---:|---:|')
for kind,table,values,coverage,missing in rows:
    print(f'| {kind} | {len(values)} | '+ ' | '.join(f'{coverage[lang]}/{len(values)}' for lang in ('en','fr','es','it'))+' |')
for kind,table,values,coverage,missing in rows:
    print(f'\n## Nicht im englischen Katalog erfasst: {kind} ({len(missing)})')
    for v in missing: print('- '+repr(v))
print('\n## Grenzen der Inventur')
print('- Zählt nur direkt als Stringliteral übergebene Konstruktor-Texte; dynamische Texte, setText-Aufrufe, Menüs, Meldungen, Tooltips und Combo-Optionen werden nicht als vollständig erfasst behauptet.')
print('- Ein vorhandener Wörterbucheintrag garantiert nicht, dass der Text im laufenden Programm aktualisiert wird.')
print('- Für die finale Freigabe sind Tests mit PySide6 auf Windows in allen fünf Sprachen nötig.')
