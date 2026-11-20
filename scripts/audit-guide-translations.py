"""Static audit of the extended guide translation coverage (no PySide6 required)."""
import ast, json, pathlib, sys
p=pathlib.Path(__file__).resolve().parents[1]/"source/workstation.py"
tree=ast.parse(p.read_text(encoding="utf-8"))
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="Workstation")
assignments={}
for node in cls.body:
    if isinstance(node,ast.Assign):
        try: val=ast.literal_eval(node.value)
        except (ValueError,TypeError,OverflowError,RecursionError): continue
        for target in node.targets:
            if isinstance(target,ast.Name): assignments[target.id]=val
# Original catalog is replaced with extended entries by a class-level update.
base=assignments["DETAILED_TAB_GUIDES"]
for node in cls.body:
    if not isinstance(node,ast.Expr) or not isinstance(node.value,ast.Call): continue
    call=node.value
    if isinstance(call.func,ast.Attribute) and call.func.attr=="update" and isinstance(call.func.value,ast.Name) and call.func.value.id=="DETAILED_TAB_GUIDES":
        try: base.update(ast.literal_eval(call.args[0]))
        except (ValueError,IndexError): pass
sources=["GUIDE_TRANSLATIONS_BY_LABEL","GUIDE_TRANSLATIONS_ALPHA20_CORE","GUIDE_TRANSLATIONS_ALPHA20_PROJECTS","GUIDE_TRANSLATIONS_ALPHA20_SUNO","MEDIA_RELEASE_GUIDE_TRANSLATIONS","ALPHA20_ALBUM_GUIDE_TRANSLATIONS","ALPHA20_BACKUP_GUIDE_TRANSLATIONS","ALPHA20_MISSING_GUIDE_TRANSLATIONS","ALPHA20_FINAL_GUIDE_TRANSLATIONS","ALPHA20_COMPLETION_GUIDE_TRANSLATIONS","ALPHA20_SUNO_EXTRA_TRANSLATIONS","ALPHA20_SUNO_PRODUCTION_TRANSLATIONS","ALPHA20_SUNO_WORKFLOW_TRANSLATIONS","GUIDE_EXTENDED_HF16"]
report={}
for name,entries in base.items():
    report[name]={}
    for lang in ("en","fr","es","it"):
        missing=[]
        for group,label,description in entries:
            found=any(lang in assignments.get(source,{}).get(name,{}).get(label,{}) for source in sources)
            if name=="Songs & Suno": found|=lang in assignments.get("GUIDE_SUNO_EXTENDED_HF14",{}).get(label,{})
            if name=="Medien & Player": found|=lang in assignments.get("ALPHA20_AUDIO_QC_GUIDE_TRANSLATIONS",{}).get(name,{}).get(label,{})
            if name=="Medien Explorer": found|=lang in assignments.get("MEDIA_EXPLORER_GUIDE_TRANSLATIONS",{}).get(label,{})
            if name=="Konfiguration": found|=lang in assignments.get("CONFIG_EXTENDED_GUIDE_TRANSLATIONS",{}).get(label,{}) or lang in assignments.get("CONFIG_ADDITIONAL_GUIDE_TRANSLATIONS",{}).get(label,{})
            if not found:missing.append(label)
        report[name][lang]={"entries":len(entries),"missing":missing}
print(json.dumps(report,ensure_ascii=False,indent=2))
if "--strict" in sys.argv and any(v["missing"] for x in report.values() for v in x.values()):sys.exit(1)
