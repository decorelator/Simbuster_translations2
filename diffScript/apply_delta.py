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

def deep_set(d, path, value):
    cur = d
    parts = path.split(".")
    for k in parts[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[parts[-1]] = value

def deep_del(d, path):
    parts = path.split(".")
    cur = d
    stack = []
    for k in parts[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            return
        stack.append((cur, k))
        cur = cur[k]
    cur.pop(parts[-1], None)
    for parent, k in reversed(stack):
        if isinstance(parent.get(k), dict) and not parent[k]:
            parent.pop(k, None)
        else:
            break

def main():
    if len(sys.argv) != 4:
        print("Usage: py apply_delta.py <es.json> <delta_es.json> <es_out.json>")
        sys.exit(2)

    es_path = Path(sys.argv[1])
    delta_path = Path(sys.argv[2])
    out_path = Path(sys.argv[3])

    es = load_json(es_path)
    delta = load_json(delta_path)

    # remove keys
    for p in delta.get("removed", []):
        deep_del(es, p)

    # apply changed + added
    for group in ("changed", "added"):
        flat = flatten(delta.get(group, {}))
        for p, v in flat.items():
            deep_set(es, p, v)

    save_json(out_path, es)
    print(f"OK: wrote {out_path}")

if __name__ == "__main__":
    main()
