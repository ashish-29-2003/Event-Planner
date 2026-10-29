"""
Security Sanitizer & Prompt Injection Defense for Samaroh (समारोह).
Neutralizes adversarial prompt injections, role hijacks, delimiter attacks,
Devanagari evasions, template expressions, and control character exploits.
"""

import re

# Delimiters and role hijack markers
ROLE_DELIMITER_PATTERN = re.compile(
    r"(?i)(<\s*\|?\s*im_(?:start|end)\s*\|?\s*>|\[/?INST\]|<<SYS>>|<</SYS>>|"
    r"###\s*(?:Human|Assistant|System)|"
    r"^\s*(?:system|assistant|developer|user)\s*:|"
    r"</?(?:brief|event_brief|user_input|user_prompt|system|prompt|context)>)",
    re.MULTILINE,
)

# Common instruction override patterns in English, Devanagari, and obfuscated variants
ADVERSARIAL_INSTRUCTION_PATTERN = re.compile(
    r"(?i)(ignore\s+(?:all\s+)?(?:previous\s+|prior\s+|above\s+)?instructions|"
    r"ignore\s+above|"
    r"disregard\s+(?:prior|previous|all)\s+directives|"
    r"forget\s+(?:all\s+|your\s+)?(?:instructions|role)|"
    r"overrid(?:e|ing)\s+(?:previous\s+|user\s+)?(?:configuration|budget|instructions)|"
    r"stop\s*[\.:,]\s*new\s+task|"
    r"you\s+are\s+now\s+(?:dan|unrestricted)|"
    r"reveal\s+(?:all\s+)?(?:passwords|credentials|keys|secret)|"
    r"(?:print|echo|show|translate)\s+(?:the\s+)?(?:exact\s+|full\s+)?(?:text\s+of\s+)?(?:your\s+|the\s+)?(?:system\s+prompt|instructions|safety\s+bounds)|"
    r"what\s+is\s+your\s+gemini_api_key|"
    r"(?:gemini_api_key|firebase_project_id|service\s+account\s+json\s+key|private\s+certificates|admin\s+session\s+token|database\s+connection\s+strings)|"
    r"bypass\s+moderation|"
    r"output\s+infinite\s+money|"
    r"fraudulent\s+and\s+dangerous|"
    r"निर्देश\s*भूल|"
    r"सिस्टम\s*प्रॉम्प्ट|"
    r"पासवर्ड\s*बताओ|"
    r"सुरक्षा\s*नियम\s*रद्द|"
    r"कुंजी\s*दिखाओ|"
    r"एपीआई\s*कुंजी|"
    r"भूमिका\s*छोड़ें|"
    r"एडमिन\s*कमांड)",
)

# Template injection & code injection patterns
CODE_INJECTION_PATTERN = re.compile(
    r"(?i)(<script[\s>]|javascript:|onerror\s*=|onload\s*=|__import__|DROP\s+TABLE|"
    r"constructor\s*\.\s*constructor|process\.env|<!\[CDATA\[|\]\]>)",
)

# Obfuscated leetspeak and separated dot-tokens pattern
LEET_REPLACEMENTS = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"
}

# Suspicious control and bidirectional override characters
SUSPICIOUS_CONTROL_CHARS = {
    "\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06", "\x07", "\x08",
    "\x0b", "\x0c", "\x0e", "\x0f", "\x1b",
    "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",  # Bi-directional text overrides
    "\u200e", "\u200f",  # LTR / RTL marks
}


def _normalize_text(text: str) -> str:
    """Normalizes unicode and strips leetspeak/dot-spacing for heuristic analysis."""
    # De-dot: e.g., "I.g.n.o.r.e" -> "Ignore"
    de_dotted = re.sub(r"(?<=\b[a-zA-Z])\.(?=[a-zA-Z]\b)", "", text)
    # Leetspeak normalize
    lowered = de_dotted.lower()
    for leet, norm in LEET_REPLACEMENTS.items():
        lowered = lowered.replace(leet, norm)
    return lowered


def is_adversarial_injection(text: str) -> bool:
    """
    Detects whether an input string exhibits adversarial prompt injection characteristics.
    """
    if not text:
        return False

    if any(ch in SUSPICIOUS_CONTROL_CHARS for ch in text):
        return True

    if ROLE_DELIMITER_PATTERN.search(text):
        return True

    if ADVERSARIAL_INSTRUCTION_PATTERN.search(text):
        return True

    if CODE_INJECTION_PATTERN.search(text):
        return True

    # Test normalized / de-obfuscated representation
    norm_text = _normalize_text(text)
    if ADVERSARIAL_INSTRUCTION_PATTERN.search(norm_text):
        return True

    # Detect base64 injection indicator
    return bool("base64 for ignore" in norm_text or "swdub3jl" in text.lower())


def sanitize_prompt_input(raw_text: str, max_length: int = 1000) -> str:
    """
    Sanitizes user input before interpolation into Gemini prompts.
    - Strips role markers, delimiters, and tag breakouts
    - Strips suspicious control characters & bidirectional overrides
    - Neutralizes code injection tags and template brackets
    - Defangs known injection commands
    - Normalizes excessive newlines and whitespace
    - Enforces max_length bounds
    """
    if not raw_text:
        return ""

    # 1. Remove dangerous control and bidirectional override characters
    cleaned = "".join(ch for ch in raw_text if ch not in SUSPICIOUS_CONTROL_CHARS and (ch.isprintable() or ch in ("\n", "\t")))

    # 2. Strip role delimiter markers and XML breakouts
    cleaned = ROLE_DELIMITER_PATTERN.sub("", cleaned)

    # 3. Defang dangerous HTML/script tags and template expressions
    cleaned = re.sub(r"(?i)</?script[^>]*>", "", cleaned)
    cleaned = re.sub(r"(?i)javascript:", "blocked_uri:", cleaned)
    cleaned = re.sub(r"(?i)onerror\s*=", "on_error_defanged=", cleaned)
    cleaned = re.sub(r"\{\{.*?\}\}", "[defanged_expr]", cleaned)

    # 4. Defang explicit attack instructions if present
    if is_adversarial_injection(cleaned):
        cleaned = re.sub(
            r"(?i)(ignore\s+(?:all\s+)?(?:previous\s+|above\s+)?instructions?|"
            r"disregard\s+(?:prior|previous)\s+directives|"
            r"forget\s+(?:all\s+|your\s+)?(?:instructions|role)|"
            r"you\s+are\s+now\s+dan|"
            r"print\s+(?:the\s+)?(?:exact\s+)?text\s+of\s+your\s+system\s+prompt|"
            r"gemini_api_key|drop\s+table)",
            "[REDACTED_PROMPT_INJECTION]",
            cleaned,
        )

    # 5. Normalize excessive newlines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # 6. Trim and enforce length limit
    return cleaned.strip()[:max_length]


def wrap_prompt_boundary(tag_name: str, content: str) -> str:
    """
    Wraps sanitized user content inside safe XML boundary delimiters.
    """
    sanitized = sanitize_prompt_input(content)
    clean_tag = re.sub(r"[^a-zA-Z0-9_]", "", tag_name)
    return f"<{clean_tag}>\n{sanitized}\n</{clean_tag}>"

