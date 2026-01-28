These .bat files are meant to be placed into your:
C:\workspace\Simbuster_translations\diffScript\

Expected structure:
- diffScript\diff_i18n.py
- diffScript\apply_delta.py
- diffScript\deltas\delta_es.json
- diffScript\deltas\delta_pt.json
- root\translations.json
- root\new_translations.json
- root\es\es.json
- root\pt\pt.json (or adjust apply_pt.bat)

Files:
- make_delta_en.bat  -> creates diffScript\deltas\delta_en.json
- apply_es.bat       -> applies diffScript\deltas\delta_es.json to es\es.json
- apply_pt.bat       -> applies diffScript\deltas\delta_pt.json to pt\... (tries common paths)
