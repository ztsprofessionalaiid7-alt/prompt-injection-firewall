import re
from bot_config import CANARY, SYSTEM_PROMPT

SECRET_PATTERNS = [
    r"AIza[0-9A-Za-z_\-]{20,}",
    r"\bsk-[A-Za-z0-9_\-]{16,}",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"(password|passwd|pwd)\s*[:=]\s*\S+",
    r"bearer\s+[A-Za-z0-9_\-\.]{20,}",
]
COMPILED = [re.compile(p, re.IGNORECASE) for p in SECRET_PATTERNS]

def _squash(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())

def _words(text: str):
    return re.sub(r"[^a-z0-9' ]", " ", text.lower()).split()

def _windows(words, n=8):
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}

PROMPT_WINDOWS = _windows(_words(SYSTEM_PROMPT))
CANARY_SQUASHED = _squash(CANARY)

def output_check(text: str):
    """ফাঁস ধরা পড়লে (True, কারণ), নইলে (False, None)"""
    if CANARY_SQUASHED in _squash(text):
        return True, "canary"
    for p in COMPILED:
        if p.search(text):
            return True, "secret pattern"
    if _windows(_words(text)) & PROMPT_WINDOWS:
        return True, "system prompt fragment"
    return False, None