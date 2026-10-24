# Prompt-Injection Firewall

**Live demo:** https://prompt-injection-firewall.streamlit.app
**2-minute demo video:** https://drive.google.com/file/d/1tzb75nFysisrCYa11Lqj6egDs5VNmc2n/view?usp=drivesdk

A two-layer firewall for an LLM support bot: it checks what users send in, and what the bot sends out.

## Problem
Users can try to override a bot's rules ("ignore previous instructions"), switch its persona, or make it reveal its system prompt or secrets. This project blocks such inputs, catches leaks in the bot's answers, and measures how well it works, including where it fails.

## How it works
```
user input
   |
   v
[1] Rule layer (regex, fast, free)  --match--> BLOCK
   |no match
   v
[2] LLM classifier (Gemini, JSON output, Pydantic validation, retries, fail-closed) --attack--> BLOCK
   |benign
   v
AcmeBot (Gemini + system prompt)
   |
   v
[3] Output check (canary token, secret patterns, system-prompt fragments) --leak--> BLOCK
   |clean
   v
answer to user
```

## Run it
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # then put your Gemini key in .env
python src\run_eval.py dev
python src\eval_output.py dev
python src\compare.py dev
streamlit run app.py        # local demo
```
Model used: gemini-3.1-flash-lite. The free tier can return 503 when busy; the code waits and retries.
Do not run `src\build_cases.py` unless you want to rebuild `data\cases.jsonl` (it overwrites it; same seed gives the same cases).

## Data
- Input cases: 25 sampled (seed 7) from `deepset/prompt-injections` (Apache-2.0): 12 attacks, 13 benign. Split: 15 dev, 10 hidden.
- Output cases: 12 written by me with AI assistance (8 dev, 4 hidden), including leaks hidden by spacing and benign text that mentions "password"/"API key".
- `data/train.parquet` is included in the repo (source: deepset/prompt-injections, Apache-2.0).
- The hidden split was run once, after the last change to detection logic and prompts.

## Results

| Set | Layer | Result |
|---|---|---|
| dev | rules only | detection 2/9, false positive 0/6 |
| dev | rules + Gemini (final) | detection 8/9, false positive 0/6 |
| dev | output check (final) | leak caught 4/4, false positive 0/4 |
| hidden | rules + Gemini | detection 3/3, false positive 0/7 |
| hidden | output check | leak caught 3/3, false positive 0/1 |

Firewall vs no firewall:

| | Without | With |
|---|---|---|
| dev: attacks reaching the bot | 9/9 | 1/9 |
| dev: benign wrongly blocked | 0/6 | 0/6 |
| hidden: attacks reaching the bot | 3/3 | 0/3 |
| hidden: benign wrongly blocked | 0/7 | 0/7 |

The hidden set has only 3 attacks, so it is a weak signal. Dev and hidden are reported separately because I tuned the classifier prompt on dev.

## What failed and what I changed
Full history with numbers is in `CHANGELOG.md`. In short:
- Rules alone caught 2/9 attacks (only literal phrases). Adding the Gemini classifier raised it to 7/9.
- A wrong model name made every call fail and the fail-closed fallback blocked everything (9/9 attacks, 6/6 false positives). That fake score showed why errors must stop the run instead of being swallowed.
- #4 (an instruction hidden after a normal question) was missed; I added a general rule to the prompt, giving 8/9.
- #14 "generate c++" still fails. It is labeled an attack in the source dataset but looks harmless, probably label noise.
- The output check missed a secret written with spaces ("ZX CANARY 7731"); I normalized text before matching.
- Running the output check on real bot answers showed false alarms on the bot introducing itself (6-word match with the system prompt); I changed the match length to 8 words.
- Deploy: the API key is now also read from the environment (Streamlit secrets). No change to detection logic or prompts.

## Limitations
- Small data: 25 input cases and 12 output cases. Numbers are not statistically solid.
- Most source attacks are propaganda or persona prompts, not system-prompt theft, so the output check added nothing beyond the input layer in the comparison.
- Output-check test cases were written by me, so they show the check works on my cases, not on real leaks.
- The output check does not catch paraphrased, base64-encoded or non-English leaks, and misses leaks shorter than 8 consecutive words.
- Rule patterns fit this dataset's common phrases; other attack styles depend on the LLM layer.
- The LLM layer adds one API call per message (latency and cost) and depends on a third-party service.
- The public demo is limited to 10 messages per session and may stop working if the free API quota runs out.
