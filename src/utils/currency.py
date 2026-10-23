"""
Indian Rupee (INR) and Lakh/Crore Number Formatting Utilities.
"""


def format_inr(amount: float) -> str:
    """
    Formats a number into standard Indian numbering grouping.
    e.g. 1250000 -> "₹12,50,000"
    """
    if amount < 0:
        return f"-₹{format_inr(-amount)[1:]}"

    amount_int = round(amount)
    s = str(amount_int)

    if len(s) <= 3:
        return f"₹{s}"

    last_three = s[-3:]
    remaining = s[:-3]

    parts = []
    while len(remaining) > 2:
        parts.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        parts.insert(0, remaining)

    parts.append(last_three)
    return f"₹{','.join(parts)}"


def format_lakhs_crores(amount: float) -> str:
    """
    Converts amount to convenient Lakhs or Crores representation.
    e.g. 4500000 -> "₹45.0 Lakh", 12500000 -> "₹1.25 Cr"
    """
    if amount >= 10_000_000:
        crores = amount / 10_000_000
        return f"₹{crores:.2f} Cr"
    elif amount >= 100_000:
        lakhs = amount / 100_000
        return f"₹{lakhs:.1f} Lakh"
    else:
        return format_inr(amount)
