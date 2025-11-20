#!/usr/bin/env python3
import json
import base64
import tkinter as tk
from tkinter import scrolledtext, messagebox
from typing import Any, Tuple, Dict, List, Set, Optional

# ========== 0. PARSING: JSON NORMALE O BASE64 ==========

def parse_json_or_base64(raw: str, label: str):
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    try:
        decoded_bytes = base64.b64decode(raw, validate=True)
        decoded_str = decoded_bytes.decode("utf-8")
        return json.loads(decoded_str)
    except Exception as e:
        raise ValueError(
            f"{label} non è né un JSON valido né un base64 contenente un JSON.\nDettagli: {e}"
        )

# ========== 1. NORMALIZZAZIONE (IGNORA ORDINE) ==========

def freeze(value: Any) -> Tuple:
    if isinstance(value, dict):
        items = sorted((k, freeze(v)) for k, v in value.items())
        return ("dict", tuple(items))
    if isinstance(value, list):
        elems = [freeze(v) for v in value]
        elems.sort()
        return ("list", tuple(elems))
    if isinstance(value, str):
        return ("str", value)
    if isinstance(value, bool):
        return ("bool", value)
    if value is None:
        return ("null", None)
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value == 0.0:
            value = 0.0
        return ("num", value)
    return ("other", repr(value))

def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: normalize(value[k]) for k in sorted(value.keys())}
    if isinstance(value, list):
        norm_elems = [normalize(v) for v in value]
        norm_elems.sort(key=freeze)
        return norm_elems
    return value

def top_level_len(value: Any) -> int:
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, list):
        return len(value)
    return 1

def compare_values(a: Any, b: Any) -> Tuple[bool, str]:
    if type(a) is not type(b):
        return False, f"Tipi top-level diversi: {type(a).__name__} vs {type(b).__name__}"

    la, lb = top_level_len(a), top_level_len(b)
    if la != lb:
        if isinstance(a, list) and isinstance(b, list):
            return False, f"Liste con dimensioni diverse: {la} vs {lb}"
        return False, f"Lunghezze top-level diverse: {la} vs {lb}"

    if freeze(a) != freeze(b):
        return False, "Contenuto diverso (ignorando l'ordine)"

    return True, "EQUAL (ignoring order and requiring same top-level length)"

# ========== 2. FORMATTAZIONE + MAPPA PATH -> RIGHE ==========

def format_with_positions(value: Any) -> Tuple[str, Dict[Tuple, List[int]]]:
    """
    Restituisce:
    - stringa formattata (JSON-like, stabile)
    - mappa: path (tuple) -> lista di indici di riga (0-based)

    I path dei container (dict, list) vengono associati
    a tutte le righe del loro contenuto, così se il diff
    segna un elemento intero (es. path (i,)) possiamo
    colorare il blocco corrispondente.
    """
    lines: List[str] = []
    positions: Dict[Tuple, List[int]] = {}

    def add_pos(path: Tuple, line_idx: int):
        positions.setdefault(path, []).append(line_idx)

    def _write(v: Any, indent: int, path: Tuple, is_last: bool):
        sp = " " * indent

        if isinstance(v, dict):
            # riga apertura dict
            line_idx_open = len(lines)
            lines.append(sp + "{")
            add_pos(path, line_idx_open)

            keys = list(v.keys())
            for idx, k in enumerate(keys):
                child = v[k]
                last_key = (idx == len(keys) - 1)
                key_repr = json.dumps(k)
                key_indent = " " * (indent + 2)
                child_path = path + (k,)

                if isinstance(child, (dict, list)):
                    line_idx = len(lines)
                    lines.append(f"{key_indent}{key_repr}:")
                    # la riga appartiene sia al campo sia al dict contenitore
                    add_pos(child_path, line_idx)
                    add_pos(path, line_idx)
                    _write(child, indent + 2, child_path, is_last=last_key)
                else:
                    val_repr = json.dumps(child)
                    line = f"{key_indent}{key_repr}: {val_repr}"
                    if not last_key:
                        line += ","
                    line_idx = len(lines)
                    lines.append(line)
                    add_pos(child_path, line_idx)
                    add_pos(path, line_idx)

            closing = sp + "}"
            if not is_last:
                closing += ","
            line_idx_close = len(lines)
            lines.append(closing)
            add_pos(path, line_idx_close)

        elif isinstance(v, list):
            # riga apertura lista
            line_idx_open = len(lines)
            lines.append(sp + "[")
            add_pos(path, line_idx_open)

            for idx, item in enumerate(v):
                last_item = (idx == len(v) - 1)
                item_path = path + (idx,)
                if isinstance(item, (dict, list)):
                    _write(item, indent + 2, item_path, is_last=last_item)
                else:
                    val_repr = json.dumps(item)
                    line = " " * (indent + 2) + val_repr
                    if not last_item:
                        line += ","
                    line_idx = len(lines)
                    lines.append(line)
                    add_pos(item_path, line_idx)
                    add_pos(path, line_idx)

            closing = sp + "]"
            if not is_last:
                closing += ","
            line_idx_close = len(lines)
            lines.append(closing)
            add_pos(path, line_idx_close)

        else:
            val_repr = json.dumps(v)
            line = sp + val_repr
            if not is_last:
                line += ","
            line_idx = len(lines)
            lines.append(line)
            add_pos(path, line_idx)

    _write(value, 0, tuple(), is_last=True)
    return "\n".join(lines), positions

# ========== 3. SCELTA AUTOMATICA DELLA CHIAVE PER LISTE DI DICT ==========

PREFERRED_KEY_NAMES = ["codPrestazione", "id", "uuid", "code", "key"]

def choose_join_key(list1: List[Any], list2: List[Any]) -> Optional[str]:
    if not (isinstance(list1, list) and isinstance(list2, list)):
        return None
    if not list1 or not list2:
        return None
    if not all(isinstance(e, dict) for e in list1 + list2):
        return None

    common_keys: Set[str] = set(list1[0].keys())
    for e in list1:
        common_keys &= set(e.keys())
    for e in list2:
        common_keys &= set(e.keys())

    if not common_keys:
        return None

    def is_unique_key(k: str, lst: List[dict]) -> bool:
        vals = []
        for e in lst:
            v = e.get(k)
            if isinstance(v, (str, int, float, bool)) or v is None:
                vals.append(v)
            else:
                return False
        return len(set(vals)) == len(vals)

    candidates = [k for k in common_keys if is_unique_key(k, list1) and is_unique_key(k, list2)]
    if not candidates:
        return None

    for pref in PREFERRED_KEY_NAMES:
        if pref in candidates:
            return pref

    return sorted(candidates)[0]

# ========== 4. DIFF BIDIREZIONALE: PATH SINISTRA / DESTRA ==========

def diff_bidir(v1: Any, v2: Any, path1: Tuple = (), path2: Tuple = ()) -> Tuple[Set[Tuple], Set[Tuple]]:
    left: Set[Tuple] = set()
    right: Set[Tuple] = set()

    if type(v1) is not type(v2):
        left.add(path1)
        right.add(path2)
        return left, right

    if isinstance(v1, dict):
        keys = set(v1.keys()) | set(v2.keys())
        for k in keys:
            p1 = path1 + (k,)
            p2 = path2 + (k,)
            if k not in v1:
                right.add(p2)
            elif k not in v2:
                left.add(p1)
            else:
                lsub, rsub = diff_bidir(v1[k], v2[k], p1, p2)
                left |= lsub
                right |= rsub
        return left, right

    if isinstance(v1, list):
        join_key = choose_join_key(v1, v2)

        if join_key is not None:
            idx1: Dict[Any, int] = {e[join_key]: i for i, e in enumerate(v1)}
            idx2: Dict[Any, int] = {e[join_key]: i for i, e in enumerate(v2)}

            keys1 = set(idx1.keys())
            keys2 = set(idx2.keys())

            for k in (keys1 & keys2):
                i1 = idx1[k]
                i2 = idx2[k]
                p1 = path1 + (i1,)
                p2 = path2 + (i2,)
                lsub, rsub = diff_bidir(v1[i1], v2[i2], p1, p2)
                left |= lsub
                right |= rsub

            for k in (keys1 - keys2):
                i1 = idx1[k]
                left.add(path1 + (i1,))

            for k in (keys2 - keys1):
                i2 = idx2[k]
                right.add(path2 + (i2,))

            return left, right

        max_len = max(len(v1), len(v2))
        for i in range(max_len):
            p1 = path1 + (i,)
            p2 = path2 + (i,)
            if i >= len(v1):
                right.add(p2)
            elif i >= len(v2):
                left.add(p1)
            else:
                lsub, rsub = diff_bidir(v1[i], v2[i], p1, p2)
                left |= lsub
                right |= rsub
        return left, right

    if v1 != v2:
        left.add(path1)
        right.add(path2)

    return left, right

# ========== 5. MOSTRA E COLORA LE RIGHE CORRISPONDENTI ==========

def show_side_by_side_diff(text1: str,
                           pos1: Dict[Tuple, List[int]],
                           text2: str,
                           pos2: Dict[Tuple, List[int]],
                           left_diff_paths: Set[Tuple],
                           right_diff_paths: Set[Tuple]):

    left_out.config(state="normal")
    right_out.config(state="normal")
    left_out.delete("1.0", tk.END)
    right_out.delete("1.0", tk.END)

    left_out.tag_configure("diff", background="#ffd6d6")
    right_out.tag_configure("diff", background="#ffd6d6")

    lines1 = text1.splitlines()
    lines2 = text2.splitlines()

    for line in lines1:
        left_out.insert(tk.END, line + "\n")

    for line in lines2:
        right_out.insert(tk.END, line + "\n")

    diff_lines_left: Set[int] = set()
    diff_lines_right: Set[int] = set()

    for p in left_diff_paths:
        if p in pos1:
            diff_lines_left.update(pos1[p])

    for p in right_diff_paths:
        if p in pos2:
            diff_lines_right.update(pos2[p])

    for idx in diff_lines_left:
        left_out.tag_add("diff", f"{idx + 1}.0", f"{idx + 1}.end")

    for idx in diff_lines_right:
        right_out.tag_add("diff", f"{idx + 1}.0", f"{idx + 1}.end")

    left_out.config(state="normal")
    right_out.config(state="normal")

# ========== 6. HANDLER BOTTONE ==========

def on_compare():
    raw1 = left_in.get("1.0", tk.END).strip()
    raw2 = right_in.get("1.0", tk.END).strip()

    if not raw1 or not raw2:
        messagebox.showwarning("Attenzione", "Inserisci entrambi i JSON (o base64) prima di confrontare.")
        return

    try:
        j1 = parse_json_or_base64(raw1, "Input 1")
    except ValueError as e:
        messagebox.showerror("Errore JSON 1", str(e))
        return

    try:
        j2 = parse_json_or_base64(raw2, "Input 2")
    except ValueError as e:
        messagebox.showerror("Errore JSON 2", str(e))
        return

    n1 = normalize(j1)
    n2 = normalize(j2)

    pretty1, pos1 = format_with_positions(n1)
    pretty2, pos2 = format_with_positions(n2)

    left_diff_paths, right_diff_paths = diff_bidir(n1, n2)

    show_side_by_side_diff(pretty1, pos1, pretty2, pos2,
                           left_diff_paths, right_diff_paths)

    equal, msg = compare_values(j1, j2)
    result_label.config(text=msg, fg="green" if equal else "red")

# ========== 7. GUI ==========

root = tk.Tk()
root.title("JSON Comparator (auto-join liste, evidenzia solo differenze, base64)")
root.geometry("1400x800")

input_frame = tk.Frame(root)
input_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

left_frame = tk.Frame(input_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
tk.Label(left_frame, text="JSON 1 (input o base64)", font=("Arial", 9, "bold")).pack(anchor="w")
left_in = scrolledtext.ScrolledText(left_frame, wrap=tk.NONE, height=12, font=("Consolas", 10))
left_in.pack(fill=tk.BOTH, expand=True)

right_frame = tk.Frame(input_frame)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
tk.Label(right_frame, text="JSON 2 (input o base64)", font=("Arial", 9, "bold")).pack(anchor="w")
right_in = scrolledtext.ScrolledText(right_frame, wrap=tk.NONE, height=12, font=("Consolas", 10))
right_in.pack(fill=tk.BOTH, expand=True)

btn = tk.Button(root, text="Confronta", font=("Arial", 11, "bold"), command=on_compare)
btn.pack(pady=5)

output_frame = tk.Frame(root)
output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

left_out_frame = tk.Frame(output_frame)
left_out_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
tk.Label(left_out_frame, text="JSON 1 normalizzato", font=("Arial", 9, "bold")).pack(anchor="w")
left_out = scrolledtext.ScrolledText(left_out_frame, wrap=tk.NONE, font=("Consolas", 10))
left_out.pack(fill=tk.BOTH, expand=True)

right_out_frame = tk.Frame(output_frame)
right_out_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
tk.Label(right_out_frame, text="JSON 2 normalizzato", font=("Arial", 9, "bold")).pack(anchor="w")
right_out = scrolledtext.ScrolledText(right_out_frame, wrap=tk.NONE, font=("Consolas", 10))
right_out.pack(fill=tk.BOTH, expand=True)

result_label = tk.Label(root, text="", font=("Arial", 11))
result_label.pack(pady=(0, 5))

root.mainloop()
