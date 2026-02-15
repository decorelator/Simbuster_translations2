import json
import sys
from pathlib import Path

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def flatten(obj, prefix="", sep="."):
    """
    Flattens nested dict into { "a.b.c": value }.
    Assumes your JSON is реально вложенный (dict внутри dict).
    """
    out = {}
    if not isinstance(obj, dict):
        return out

    for k, v in obj.items():
        p = f"{prefix}{sep}{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, p, sep=sep))
        else:
            out[p] = v
    return out

def main():
    if len(sys.argv) != 4:
        print("Usage: python diff_i18n.py <en_old.json> <en_new.json> <delta_out.json>")
        sys.exit(2)

    en_old_path = Path(sys.argv[1])
    en_new_path = Path(sys.argv[2])
    out_path = Path(sys.argv[3])

    old = flatten(load_json(en_old_path))
    new = flatten(load_json(en_new_path))

    oldk = set(old.keys())
    newk = set(new.keys())

    added   = {k: new[k] for k in sorted(newk - oldk)}
    removed = sorted(oldk - newk)
    changed = {k: new[k] for k in sorted(newk & oldk) if old[k] != new[k]}

    # ВАЖНО: added/changed сохраняем ПЛОСКО (без unflatten), чтобы не ловить коллизии
    delta = {
        "added": added,
        "changed": changed,
        "removed": removed
    }

    save_json(out_path, delta)
    print(f"OK: wrote {out_path}")
    print(f"Added: {len(added)}, Changed: {len(changed)}, Removed: {len(removed)}")

if __name__ == "__main__":
    main()
