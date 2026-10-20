import json, sys, time
from rules import rule_check
from classifier import classify
from output_check import output_check
from bot import ask_bot

split = sys.argv[1] if len(sys.argv) > 1 else "dev"
cases = [json.loads(l) for l in open("data/cases.jsonl", encoding="utf-8")]
cases = [c for c in cases if c["split"] == split]

rows = []
for c in cases:
    answer = ask_bot(c["input"]); time.sleep(4)
    in_block = rule_check(c["input"])[0]
    if not in_block:
        in_block = classify(c["input"]).label == "attack"; time.sleep(4)
    out_block = output_check(answer)[0]
    rows.append({"tag": c["tag"], "in": in_block, "out": out_block})
    print(c["id"], c["tag"], "input-block" if in_block else "-",
          "output-block" if out_block else "-")

atk = [r for r in rows if r["tag"] == "attack"]
ben = [r for r in rows if r["tag"] == "benign"]

def n(rs, f): return sum(1 for r in rs if f(r))

print(f"\n=== {split} ===")
print("WITHOUT firewall: attacks blocked 0/%d, benign blocked 0/%d, bot answers containing a leak: %d/%d"
      % (len(atk), len(ben), n(rows, lambda r: r["out"]), len(rows)))
print("WITH firewall:")
print("  attacks blocked at input : %d/%d" % (n(atk, lambda r: r["in"]), len(atk)))
print("  attacks blocked at output only: %d/%d" % (n(atk, lambda r: not r["in"] and r["out"]), len(atk)))
print("  attacks passed through   : %d/%d" % (n(atk, lambda r: not r["in"] and not r["out"]), len(atk)))
print("  benign wrongly blocked   : %d/%d" % (n(ben, lambda r: r["in"] or r["out"]), len(ben)))