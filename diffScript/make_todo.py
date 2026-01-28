import json
import sys
from pathlib import Path

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    if len(sys.argv) != 3:
        print("Usage: py make_todo.py <delta_en.json> <delta_es_todo.json>")
        sys.exit(2)

    delta_en = load_json(Path(sys.argv[1]))

    # todo-файл: только то, что надо перевести + служебное
    todo = {
        "added": delta_en.get("added", {}),
        "changed": delta_en.get("changed", {}),
        "removed": delta_en.get("removed", [])
    }

    save_json(Path(sys.argv[2]), todo)
    print(f"OK: wrote {sys.argv[2]}")

if __name__ == "__main__":
    main()
