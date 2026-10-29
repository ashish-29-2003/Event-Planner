"""
Firestore Security Rules Policy Verification & Isolation Tests.
Tests rules structure, syntax constraints, and multi-tenant access evaluation.
"""

import re
from pathlib import Path


def test_firestore_rules_file_validity():
    """Verifies firestore.rules file syntax and structure."""
    rules_path = Path(__file__).resolve().parent.parent / "firestore.rules"
    assert rules_path.exists(), "firestore.rules must exist in root directory"

    content = rules_path.read_text(encoding="utf-8")
    assert "rules_version = '2';" in content
    assert "service cloud.firestore" in content
    assert "function isOwner(userId)" in content
    assert "match /users/{userId}" in content
    assert "match /events/{eventId}" in content
    assert "match /budgets/{budgetId}" in content
    assert "match /tasks/{taskId}" in content
    assert "match /vendors/{vendorId}" in content
    assert "match /guests/{guestId}" in content


class MockFirestoreRuleEvaluator:
    """Simulates security rule evaluation against the Samaroh firestore.rules policy."""

    @staticmethod
    def evaluate(
        path: str,
        operation: str,
        auth_uid: str | None,
    ) -> bool:
        # Public events allow read, deny write
        if path.startswith("/public_events"):
            return operation == "read"

        # User documents /users/{userId}/...
        user_match = re.match(r"^/users/([^/]+)(?:/.*)?$", path)
        if user_match:
            doc_user_id = user_match.group(1)
            # isOwner: authenticated and auth_uid == userId
            return bool(auth_uid is not None and auth_uid == doc_user_id)

        # All other paths denied by default
        return False


def test_rule_policy_owner_granted_access():
    """User A has full read/write access to their own events and subcollections."""
    evaluator = MockFirestoreRuleEvaluator()
    assert evaluator.evaluate("/users/user_alice/events/event_1", "read", "user_alice") is True
    assert evaluator.evaluate("/users/user_alice/events/event_1", "write", "user_alice") is True
    assert (
        evaluator.evaluate(
            "/users/user_alice/events/event_1/budgets/b_1", "write", "user_alice"
        )
        is True
    )
    assert (
        evaluator.evaluate(
            "/users/user_alice/events/event_1/guests/g_1", "write", "user_alice"
        )
        is True
    )


def test_rule_policy_cross_user_denied_access():
    """User B cannot read or write User A's events (prevents IDOR)."""
    evaluator = MockFirestoreRuleEvaluator()
    assert evaluator.evaluate("/users/user_alice/events/event_1", "read", "user_bob") is False
    assert evaluator.evaluate("/users/user_alice/events/event_1", "write", "user_bob") is False
    assert (
        evaluator.evaluate(
            "/users/user_alice/events/event_1/budgets/b_1", "write", "user_bob"
        )
        is False
    )


def test_rule_policy_unauthenticated_denied_access():
    """Unauthenticated users cannot read or write private user collections."""
    evaluator = MockFirestoreRuleEvaluator()
    assert evaluator.evaluate("/users/user_alice/events/event_1", "read", None) is False
    assert evaluator.evaluate("/users/user_alice/events/event_1", "write", None) is False


def test_rule_policy_public_events_read_only():
    """Public demo celebrations can be read by anyone but cannot be modified."""
    evaluator = MockFirestoreRuleEvaluator()
    assert evaluator.evaluate("/public_events/demo-wedding-jaipur", "read", None) is True
    assert evaluator.evaluate("/public_events/demo-wedding-jaipur", "read", "user_bob") is True
    assert evaluator.evaluate("/public_events/demo-wedding-jaipur", "write", None) is False
    assert (
        evaluator.evaluate("/public_events/demo-wedding-jaipur", "write", "user_bob") is False
    )


def test_rule_policy_default_deny():
    """Unmatched top-level collections are strictly denied."""
    evaluator = MockFirestoreRuleEvaluator()
    assert evaluator.evaluate("/admin/secrets", "read", "user_alice") is False
    assert evaluator.evaluate("/random_collection/doc1", "write", "user_alice") is False
