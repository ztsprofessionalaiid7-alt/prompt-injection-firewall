import json, sys, time
from rules import rule_check
from classifier import classify

split = sys.argv[1] if len(sys.argv) > 1 else "dev"
cases = [json.loads(l) for l in open("data/cases.jsonl", encoding="utf-8")]
cases = [c for c in cases if c["split"] == split]

def firewall(text):
    hit, _ = rule_check(text)
    if hit:
        return "block", "rule"
    v = classify(text)
    time.sleep(4)  # ফ্রি টিয়ারের রেট লিমিটের জন্য
    return ("block" if v.label == "attack" else "allow"), "llm"

tp = fp = fn = tn = 0
for c in cases:
    got, layer = firewall(c["input"])
    ok = got == c["expected"]
    if c["expected"] == "block":
        tp += ok; fn += (not ok)
    else:
        tn += ok; fp += (not ok)
    print("PASS" if ok else "FAIL", c["id"], c["tag"], layer, "|", c["input"][:60])

print(f"\n{split}: detection {tp}/{tp+fn}, false positive {fp}/{tn+fp}")