import json
import sys
from pathlib import Path

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def flatten(obj, prefix=""):
    out = {}
    if not isinstance(obj, dict):
        return out
    for k, v in obj.items():
        p = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, p))
        else:
            out[p] = v
    return out

def unflatten(flat_map):
    root = {}
    for path, val in flat_map.items():
        cur = root
        parts = path.split(".")
        for key in parts[:-1]:
            cur = cur.setdefault(key, {})
        cur[parts[-1]] = val
    return root

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

    added = {k: new[k] for k in sorted(newk - oldk)}
    removed = sorted(oldk - newk)
    changed = {k: new[k] for k in sorted(newk & oldk) if old[k] != new[k]}

    delta = {
        "added": unflatten(added),
        "changed": unflatten(changed),
        "removed": removed
    }

    save_json(out_path, delta)
    print(f"OK: wrote {out_path}")
    print(f"Added: {len(added)}, Changed: {len(changed)}, Removed: {len(removed)}")

if __name__ == "__main__":
    main()
