import json, sys
from typing import List, Tuple

def load_jsonl(path: str) -> List[dict]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                items.append(obj)
            except Exception as e:
                print(f"[WARN] Failed to parse line {ln}, skipped: {e}", file=sys.stderr)
    return items

def extract_pairs(items: List[dict], key_field: str, value_field: str) -> List[Tuple[str, object, int]]:
    pairs = []
    for i, obj in enumerate(items):
        if key_field in obj and value_field in obj:
            pairs.append((str(obj[key_field]), obj[value_field], i))
        elif len(obj) == 2:
            ks = list(obj.keys())
            pairs.append((str(obj[ks[0]]), obj[ks[1]], i))
        else:
            pass
    return pairs

def extract_memory(role:str,recent_k:int,memory_path):
    with open(memory_path,'r',encoding='utf-8') as f:
        memory_list=[json.loads(line) for line in f if line.strip()]

    memory_list=[memory for memory in memory_list if memory.get("role")==role]
    memory_list=memory_list[-recent_k:]

    return memory_list