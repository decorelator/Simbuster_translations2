import json
import sys
from pathlib import Path

SEP = "."
CONFLICTS_FILE = "conflicts.txt"

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

# -------- schema traversal (treat keys as literal, even if they contain dots) --------
def schema_leaf_paths(schema_obj: dict, prefix_keys=None):
    """
    Yields paths as list of literal keys exactly as in schema.
    Example leaf: ["esim","guide-steps","pay","title.samsung"]
    """
    if prefix_keys is None:
        prefix_keys = []
    if not isinstance(schema_obj, dict):
        return
    for k, v in schema_obj.items():
        p = prefix_keys + [k]
        if isinstance(v, dict):
            yield from schema_leaf_paths(v, p)
        else:
            yield p

def get_by_keys(obj, keys):
    cur = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None, False
        cur = cur[k]
    return cur, True

def set_by_keys(obj, keys, value):
    cur = obj
    for k in keys[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[keys[-1]] = value

def del_by_keys(obj, keys):
    cur = obj
    stack = []
    for k in keys[:-1]:
        if not isinstance(cur, dict) or k not in cur or not isinstance(cur[k], dict):
            return
        stack.append((cur, k))
        cur = cur[k]
    if isinstance(cur, dict):
        cur.pop(keys[-1], None)

    # cleanup empties
    for parent, k in reversed(stack):
        if isinstance(parent.get(k), dict) and not parent[k]:
            parent.pop(k, None)
        else:
            break

# -------- dotted delta key -> literal schema keys (greedy match) --------
def resolve_path(schema_obj: dict, dotted_key: str):
    """
    Converts "a.b.c.d" -> ["a","b","c","d"] BUT if schema has "c.d" as one key,
    it resolves as ["a","b","c.d"].
    Greedy longest-match at each level.
    """
    parts = dotted_key.split(SEP)
    cur = schema_obj
    resolved = []
    i = 0

    while i < len(parts):
        if not isinstance(cur, dict):
            resolved.extend(parts[i:])
            break

        found = False
        for n in range(len(parts) - i, 0, -1):
            cand = SEP.join(parts[i:i+n])
            if cand in cur:
                resolved.append(cand)
                cur = cur[cand]
                i += n
                found = True
                break

        if not found:
            # fallback: single segment
            resolved.append(parts[i])
            cur = cur.get(parts[i]) if isinstance(cur, dict) else None
            i += 1

    return resolved

# -------- normalize legacy "__value" objects back to flat keys (schema-driven) --------
def extract_legacy_value(locale_obj, schema_leaf_keys):
    """
    For schema leaf key like "...pay.title.samsung":
      1) Try exact key in locale (title.samsung).
      2) If not found, try legacy form:
         title is dict and contains 'samsung' -> use that
    For schema leaf key like "...pay.title":
      1) exact key title
      2) if title is dict and contains '__value' -> use __value
    """
    leaf = schema_leaf_keys[-1]
    parent_keys = schema_leaf_keys[:-1]

    parent, ok = get_by_keys(locale_obj, parent_keys)
    if not ok or not isinstance(parent, dict):
        return None, False

    # 1) exact
    if leaf in parent and not isinstance(parent[leaf], dict):
        return parent[leaf], True

    # 2) legacy unwrap
    if SEP in leaf:
        base, suffix = leaf.rsplit(SEP, 1)
        base_val = parent.get(base)
        if isinstance(base_val, dict) and suffix in base_val and not isinstance(base_val[suffix], dict):
            return base_val[suffix], True
    else:
        base_val = parent.get(leaf)
        if isinstance(base_val, dict) and "__value" in base_val and not isinstance(base_val["__value"], dict):
            return base_val["__value"], True

    return None, False

def normalize_locale_to_schema(locale_obj: dict, schema_obj: dict):
    """
    Builds a new locale tree that follows schema keys exactly.
    It pulls values from existing locale (including legacy __value style).
    Leaves missing values untouched (not added) — delta will add what it needs.
    """
    out = {}
    for keys in schema_leaf_paths(schema_obj):
        val, ok = extract_legacy_value(locale_obj, keys)
        if ok:
            set_by_keys(out, keys, val)
    return out

# -------- apply delta (flat) into nested locale using schema resolver --------
def apply_delta(locale_obj: dict, schema_obj: dict, delta: dict, conflicts: list):
    # removed
    removed = delta.get("removed", [])
    if isinstance(removed, list):
        for dk in removed:
            if not isinstance(dk, str):
                continue
            keys = resolve_path(schema_obj, dk)
            del_by_keys(locale_obj, keys)

    # changed + added
    for group in ("changed", "added"):
        mp = delta.get(group, {})
        if not isinstance(mp, dict):
            continue
        for dk, v in mp.items():
            if not isinstance(dk, str):
                continue
            keys = resolve_path(schema_obj, dk)
            if dk != SEP.join(keys):
                conflicts.append(f"RESOLVE: '{dk}' -> {keys}")
            set_by_keys(locale_obj, keys, v)

def main():
    if len(sys.argv) != 5:
        print("Usage: py apply_delta.py <new_translations.json> <locale_in.json> <delta.json> <locale_out.json>")
        sys.exit(2)

    schema_path = Path(sys.argv[1])
    locale_in_path = Path(sys.argv[2])
    delta_path = Path(sys.argv[3])
    locale_out_path = Path(sys.argv[4])

    schema = load_json(schema_path)
    locale_raw = load_json(locale_in_path)
    delta = load_json(delta_path)

    if not isinstance(schema, dict):
        raise TypeError("new_translations.json must be a top-level JSON object")
    if not isinstance(locale_raw, dict):
        raise TypeError("locale_in.json must be a top-level JSON object")
    if not isinstance(delta, dict):
        raise TypeError("delta.json must be a top-level JSON object")

    conflicts = []

    # 1) normalize legacy __value objects back into schema-shaped locale
    locale = normalize_locale_to_schema(locale_raw, schema)

    # 2) apply delta correctly (keeping keys like 'title.samsung' as literal keys)
    apply_delta(locale, schema, delta, conflicts)

    # conflicts.txt in project root (parent of diffScript)
    conflicts_path = Path(__file__).resolve().parent.parent / CONFLICTS_FILE
    conflicts_path.write_text("\n".join(conflicts), encoding="utf-8")

    # atomic write
    tmp = locale_out_path.with_suffix(locale_out_path.suffix + ".tmp")
    save_json(tmp, locale)
    tmp.replace(locale_out_path)

    print(f"OK: wrote {locale_out_path}")
    print(f"Conflicts: {len(conflicts)} -> {conflicts_path}")

if __name__ == "__main__":
    main()
