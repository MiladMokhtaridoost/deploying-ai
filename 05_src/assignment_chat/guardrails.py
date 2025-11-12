import re

# Simple leakage & jailbreak patterns
PROMPT_LEAK_PATTERNS = [
    r"(?i)\b(system prompt|show.*prompt|reveal.*prompt)\b",
    r"(?i)\bignore (all|previous) instructions\b",
    r"(?i)\b(jailbreak|bypass|ignore guardrails)\b",
]

# Disallowed topics
BLOCK_TOPICS = r"(?i)\b(cat|cats|dog|dogs|horoscope|zodiac|taylor swift)\b"

def check_guardrails(user_text: str):
    # Block topic
    if re.search(BLOCK_TOPICS, user_text or ""):
        return True, "disallowed topic"
    # Prompt leakage attempts
    for pat in PROMPT_LEAK_PATTERNS:
        if re.search(pat, user_text or ""):
            return True, "prompt leakage attempt"
    return False, ""

