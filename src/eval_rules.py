import json, sys
from rules import rule_check

split = sys.argv[1] if len(sys.argv) > 1 else "dev"
cases = [json.loads(l) for l in open("data/cases.jsonl", encoding="utf-8")]
cases = [c for c in cases if c["split"] == split]

tp = fp = fn = tn = 0
for c in cases:
    hit, pat = rule_check(c["input"])
    got = "block" if hit else "allow"
    ok = got == c["expected"]
    if c["expected"] == "block":
        tp += ok; fn += (not ok)
    else:
        tn += ok; fp += (not ok)
    if not ok:
        print("FAIL", c["id"], c["tag"], "|", c["input"][:70])

atk = tp + fn
ben = tn + fp
print(f"\n{split}: detection {tp}/{atk}, false positive {fp}/{ben}")