#!/usr/bin/env python3
"""Static startup initialization audit. Does not import PySide6 or touch user data."""
import argparse
import ast
import json
from pathlib import Path


def audit(source):
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Workstation')
    methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    init = methods['__init__']
    initialized = set()
    issues = []
    built = []
    # Inspect statements in the actual constructor order, including nested build calls.
    def visit(method_name, active):
        if method_name in active or method_name not in methods:
            return
        body = methods[method_name].body
        for stmt in body:
            # Only direct statement order; do not assume conditionals always run.
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                for target in targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                        initialized.add(target.attr)
            for node in ast.walk(stmt):
                if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name) and node.value.value.id == 'self' and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                    # Read-only subscript is risky if the dictionary is not yet initialized.
                    if isinstance(stmt, ast.Assign) and node in stmt.targets:
                        continue
                    if node.value.attr in ('config_extra_p34', 'appearance_text_p35') and node.value.attr not in initialized:
                        issues.append({'method':method_name,'line':node.lineno,'attribute':node.value.attr,'problem':'access before initialization'})
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Attribute) and isinstance(stmt.value.func.value, ast.Name) and stmt.value.func.value.id == 'self':
                called = stmt.value.func.attr
                if called.startswith('build_'):
                    built.append(called)
                    visit(called, active | {method_name})
    visit('__init__', set())
    return {'build_methods':built,'build_count':len(built),'issues':issues}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[1]/'source'/'workstation.py')
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args()
    result=audit(args.source.read_text(encoding='utf-8'))
    print(json.dumps(result,indent=2,ensure_ascii=False) if args.json else f"Startup audit: {result['build_count']} build calls, {len(result['issues'])} issues")
    return 1 if result['issues'] else 0

if __name__=='__main__':
    raise SystemExit(main())
