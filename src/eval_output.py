import json, sys
from output_check import output_check

split = sys.argv[1] if len(sys.argv) > 1 else "dev"
cases = [json.loads(l) for l in open("data/output_cases.jsonl", encoding="utf-8")]
cases = [c for c in cases if c["split"] == split]

tp = fp = fn = tn = 0
for c in cases:
    hit, why = output_check(c["output"])
    got = "block" if hit else "allow"
    ok = got == c["expected"]
    if c["expected"] == "block":
        tp += ok; fn += (not ok)
    else:
        tn += ok; fp += (not ok)
    print("PASS" if ok else "FAIL", c["id"], c["tag"], why, "|", c["output"][:60])

print(f"\n{split}: leak caught {tp}/{tp+fn}, false positive {fp}/{tn+fp}")