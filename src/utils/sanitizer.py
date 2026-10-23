"""
Security Sanitizer for GenAI Prompts & User Inputs.
Prevents prompt injection, system overrides, and control character exploits.
"""
import re

def sanitize_prompt_input(raw_text: str, max_length: int = 1000) -> str:
    """
    Sanitizes user input before interpolation into Gemini prompts.
    - Strips markdown system instructions & delimiters
    - Truncates to max_length
    - Normalizes excessive whitespace
    """
    if not raw_text:
        return ""
    
    # Strip potential prompt injection headers
    cleaned = re.sub(r'(?i)(system:|assistant:|developer:|user:|\[INST\]|\[/INST\])', '', raw_text)
    
    # Strip control characters except newline and tab
    cleaned = "".join(ch for ch in cleaned if ch.isprintable() or ch in ('\n', '\t'))
    
    # Normalize excessive newlines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Strip and enforce length boundary
    return cleaned.strip()[:max_length]
