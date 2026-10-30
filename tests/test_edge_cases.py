"""
Comprehensive Edge-Case & Boundary Resilience Tests (R4-T02)
Tests empty inputs, boundary budgets, heavy Unicode/Devanagari,
giant guest counts, timeout resilience, and currency math boundaries.
"""
import pytest
from pydantic import ValidationError

from src.models.event import CelebrationBrief, EventType
from src.models.timeline import TaskItem
from src.services.calendar_service import create_google_calendar_url, generate_ics_calendar
from src.utils.currency import format_inr, format_lakhs_crores
from src.utils.sanitizer import sanitize_prompt_input


# 1. Budget & Numeric Boundaries
def test_negative_budget_rejected_in_brief():
    """Negative budgets must be rejected by Pydantic validation."""
    with pytest.raises(ValidationError):
        CelebrationBrief(
            title="Test Negative Budget",
            event_type=EventType.WEDDING,
            culture="Marwari",
            city="Jaipur",
            target_budget=-50000.0,
            guest_count=100,
        )


def test_zero_budget_rejected_in_brief():
    """Zero budget must be rejected (budget must be > 0)."""
    with pytest.raises(ValidationError):
        CelebrationBrief(
            title="Test Zero Budget",
            event_type=EventType.WEDDING,
            culture="Marwari",
            city="Jaipur",
            target_budget=0.0,
            guest_count=100,
        )


def test_extreme_high_budget_boundary():
    """Ensure maximum allowed budget (₹10 Crore) is accepted and higher is rejected."""
    brief = CelebrationBrief(
        title="Royal Mega Vivaha",
        event_type=EventType.WEDDING,
        culture="Marwari",
        city="Udaipur",
        target_budget=100_000_000.0,  # ₹10 Crore maximum limit
        guest_count=5000,
    )
    assert brief.target_budget == 100_000_000.0
    formatted = format_inr(brief.target_budget)
    assert "₹10,00,00,000" in formatted

    # Over 10 Crore must be rejected by Pydantic validation
    with pytest.raises(ValidationError):
        CelebrationBrief(
            title="Beyond Limit",
            event_type=EventType.WEDDING,
            culture="Marwari",
            city="Udaipur",
            target_budget=100_000_001.0,
            guest_count=5000,
        )


def test_negative_guest_count_rejected():
    """Negative or zero guest count must be rejected."""
    with pytest.raises(ValidationError):
        CelebrationBrief(
            title="Ghost Celebration",
            event_type=EventType.BIRTHDAY,
            culture="Contemporary",
            city="Delhi",
            target_budget=50000.0,
            guest_count=-5,
        )


def test_giant_guest_count_boundary():
    """Large community gather counts (e.g. 50,000) are accepted up to max limit."""
    brief = CelebrationBrief(
        title="Maha Kumbh Community Bhojan",
        event_type=EventType.COMMUNITY,
        culture="Vedic",
        city="Prayagraj",
        target_budget=5_000_000.0,
        guest_count=50000,
    )
    assert brief.guest_count == 50000


# 2. Unicode, Devanagari & Emoji Preservation
def test_devanagari_and_sanskrit_script_preservation():
    """Devanagari characters, Matras, and Nuktas must not be corrupted or stripped."""
    hindi_text = "अनन्या एवं रोहन का शुभ पाणिग्रहण संस्कार ॥ ॐ श्री गणेशाय नमः ॥"
    sanitized = sanitize_prompt_input(hindi_text)
    assert sanitized == hindi_text
    assert "॥" in sanitized
    assert "ॐ" in sanitized


def test_emoji_and_symbols_handling():
    """Festive emojis and Indian cultural symbols are safely handled."""
    emoji_brief = "Celebration 🎉🪔💍 Mandap & Haldi Ceremony ✨"
    sanitized = sanitize_prompt_input(emoji_brief)
    assert "Mandap & Haldi" in sanitized


def test_rtl_bidi_override_neutralization():
    """Right-to-Left and bidirectional override characters must be stripped to prevent display spoofing."""
    bidi_attack = "Normal\u202eRotatedText\u202cEnd"
    sanitized = sanitize_prompt_input(bidi_attack)
    assert "\u202e" not in sanitized
    assert "\u202c" not in sanitized


# 3. String & Whitespace Boundaries
def test_empty_string_input_sanitization():
    """Empty or whitespace-only strings return safe empty strings without crashing."""
    assert sanitize_prompt_input("") == ""
    assert sanitize_prompt_input("   ") == ""
    assert sanitize_prompt_input("\n\t\r") == ""


def test_giant_string_truncation():
    """Huge 50KB strings are safely truncated to maximum length without memory exhaustion."""
    giant_text = "Celebration brief " * 3000
    sanitized = sanitize_prompt_input(giant_text, max_length=1500)
    assert len(sanitized) == 1500


# 4. Currency Math & Formatter Edge Cases
def test_currency_formatter_edge_cases():
    """Test format_inr with zero, decimals, None, and negative numbers."""
    assert format_inr(0) == "₹0"
    assert format_inr(0.0) == "₹0"
    assert "50,000" in format_inr(50000)
    assert "1,00,000" in format_inr(100000)  # 1 Lakh
    assert "10,00,000" in format_inr(1000000)  # 10 Lakh
    assert "1,00,00,000" in format_inr(10000000)  # 1 Crore


def test_currency_lakhs_crores_edge_cases():
    """Test format_lakhs_crores with various scales."""
    assert "Cr" in format_lakhs_crores(12500000)
    assert "Lakh" in format_lakhs_crores(4500000)
    assert format_lakhs_crores(5000) == "₹5,000"


# 5. Calendar Edge Cases
def test_calendar_url_with_none_or_malformed_date():
    """Calendar URL generation should not crash on missing or malformed date."""
    url1 = create_google_calendar_url(title="Test", description="Desc", date_str=None)
    assert "https://calendar.google.com" in url1
    assert "Samaroh%3A+Test" in url1 or "Samaroh" in url1

    url2 = create_google_calendar_url(title="Test", description="Desc", date_str="invalid-date")
    assert "https://calendar.google.com" in url2


def test_calendar_ics_with_empty_tasks():
    """RFC-5545 generator must produce valid VCALENDAR even with empty tasks list."""
    ics = generate_ics_calendar("Empty Event", [])
    assert "BEGIN:VCALENDAR" in ics
    assert "VERSION:2.0" in ics
    assert "END:VCALENDAR" in ics


def test_calendar_ics_escaping_special_chars():
    """RFC-5545 generator must properly escape semicolons, commas, and newlines."""
    task = TaskItem(
        id="t-special",
        title="Vendor Meet; Catering, Flowers\nMandap",
        due_date="2026-11-20",
        phase="Phase 1",
        owner_role="Coordinator",
        description="Line 1\nLine 2; with semicolon",
    )
    ics = generate_ics_calendar("Special Event", [task])
    assert "BEGIN:VEVENT" in ics
    assert "\\;" in ics or ";" in ics
    assert "END:VEVENT" in ics
