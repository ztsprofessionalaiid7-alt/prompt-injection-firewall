import re

# প্রতিটা প্যাটার্ন একটা চেনা আক্রমণের ধরন ধরে
PATTERNS = [
    # নির্দেশ উপেক্ষা করানো (ইংরেজি)
    r"ignore (all |any |the )?(previous|above|prior|earlier|your)\b.{0,20}(instructions|rules|prompts?|guidelines)",
    r"disregard (your|all|the|any)\b.{0,20}(instructions|rules|guidelines)",
    r"forget (everything|all|your)\b.{0,20}(instructions|rules|above|before)",
    # সিস্টেম প্রম্পট বা গোপন তথ্য বের করা
    r"(reveal|print|show|repeat|output|leak).{0,40}(system prompt|hidden rules|your instructions)",
    r"(api key|password|secret token|credentials)",
    # জেলব্রেক ও পারসোনা
    r"\bDAN\b|developer mode|jailbreak|no restrictions|without (any )?(filters|restrictions)",
    r"you are now\b.{0,40}(ai|bot|assistant)",
    # জার্মান (ডেটাসেটে মিশ্র থাকে)
    r"vergiss (alles|alle)|ignoriere (alle|die) (vorherigen|obigen)",
    # বাংলা
    r"আগের (সব )?(নির্দেশ|নিয়ম).{0,15}(ভুলে|উপেক্ষা)",
    r"সিস্টেম প্রম্পট",
]

COMPILED = [re.compile(p, re.IGNORECASE) for p in PATTERNS]


def rule_check(text: str):
    """ধরা পড়লে (True, প্যাটার্ন), নইলে (False, None)"""
    for p in COMPILED:
        if p.search(text):
            return True, p.pattern
    return False, None