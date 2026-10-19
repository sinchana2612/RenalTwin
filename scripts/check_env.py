import sys, importlib
mods=["numpy","pandas","sklearn","fastapi","sqlalchemy","lightgbm"]
print("Python",sys.version)
failed=[]
for m in mods:
 try: importlib.import_module(m); print(m,"OK")
 except Exception as e: print(m,"MISSING",e); failed.append(m)
print("Environment check complete; optional lightgbm is not required by this implementation.")
