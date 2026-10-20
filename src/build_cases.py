import json, random
import pandas as pd

random.seed(7)
df = pd.read_parquet("data/train.parquet")
df = df[df["text"].str.len() < 200]

att = df[df["label"] == 1]["text"].tolist()
ben = df[df["label"] == 0]["text"].tolist()

rows  = [(t, "block", "attack") for t in random.sample(att, 12)]
rows += [(t, "allow", "benign") for t in random.sample(ben, 13)]
random.shuffle(rows)

with open("data/cases.jsonl", "w", encoding="utf-8") as f:
    for i, (text, exp, tag) in enumerate(rows, 1):
        f.write(json.dumps({
            "id": i, "input": text, "expected": exp, "tag": tag,
            "split": "dev" if i <= 15 else "hidden",
        }, ensure_ascii=False) + "\n")
print("done:", len(rows), "cases")