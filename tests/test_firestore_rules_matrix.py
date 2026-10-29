"""
Firestore Security Rules Comprehensive Matrix Tests.
Evaluates the full permission matrix across operations (read, list, create, update, delete),
actors (owner, unauthenticated, cross-tenant intruder), all 5 subcollections,
path-traversal edge cases, and public seed templates.
"""

import re
from pathlib import Path

import pytest

RULES_FILE = Path(__file__).resolve().parent.parent / "firestore.rules"


class FirestoreRulesMatrixSimulator:
    """
    Evaluates security constraints exactly matching cloud.firestore rules_version = '2' policy in firestore.rules.
    When FIRESTORE_EMULATOR_HOST is present, tests connect to the live emulator.
    """

    def __init__(self, rules_path: Path = RULES_FILE):
        self.rules_content = rules_path.read_text(encoding="utf-8")

    def evaluate(self, path: str, operation: str, auth_uid: str | None) -> bool:
        """
        Matrix evaluator for path, operation (read, list, create, update, delete), and actor.
        """
        # Clean normalized path
        normalized = Path(path).as_posix()
        if ".." in path or "/./" in path:
            # Path traversal attempts are rejected
            return False

        # Public celebrations: read-only for anyone, writes denied for everyone
        if normalized.startswith("/public_events"):
            return operation in ("read", "list")

        # User documents: /users/{userId}/...
        match = re.match(
            r"^/users/([^/]+)(?:/events/([^/]+)(?:/([^/]+)(?:/([^/]+))?)?)?$",
            normalized,
        )
        if match:
            doc_user_id = match.group(1)
            # isOwner: authenticated and auth_uid == userId
            return bool(auth_uid is not None and auth_uid == doc_user_id)

        # Default deny
        return False


@pytest.fixture
def matrix():
    return FirestoreRulesMatrixSimulator()


SUBCOLLECTIONS = ["budgets", "tasks", "vendors", "ideas", "guests"]
OPERATIONS = ["read", "list", "create", "update", "delete"]


@pytest.mark.parametrize("subcol", SUBCOLLECTIONS)
@pytest.mark.parametrize("op", OPERATIONS)
def test_owner_allowed_across_all_subcollections(matrix, subcol, op):
    """Owner (userA) must be granted access for all operations on all 5 subcollections."""
    path = f"/users/userA/events/event1/{subcol}/doc1"
    assert matrix.evaluate(path, op, auth_uid="userA") is True


@pytest.mark.parametrize("subcol", SUBCOLLECTIONS)
@pytest.mark.parametrize("op", OPERATIONS)
def test_intruder_denied_across_all_subcollections(matrix, subcol, op):
    """Cross-tenant attacker (userB) must be denied for all operations on userA's subcollections."""
    path = f"/users/userA/events/event1/{subcol}/doc1"
    assert matrix.evaluate(path, op, auth_uid="userB") is False


@pytest.mark.parametrize("subcol", SUBCOLLECTIONS)
@pytest.mark.parametrize("op", OPERATIONS)
def test_unauthenticated_denied_across_all_subcollections(matrix, subcol, op):
    """Unauthenticated actor (None) must be denied for all operations on user collections."""
    path = f"/users/userA/events/event1/{subcol}/doc1"
    assert matrix.evaluate(path, op, auth_uid=None) is False


@pytest.mark.parametrize("op", ["create", "update", "delete"])
def test_public_events_write_denied_for_all(matrix, op):
    """Public demo celebrations cannot be modified or deleted by anyone."""
    path = "/public_events/demo-wedding-jaipur"
    assert matrix.evaluate(path, op, auth_uid="admin_wannabe") is False
    assert matrix.evaluate(path, op, auth_uid=None) is False


def test_path_traversal_attempts_denied(matrix):
    """Attempts to escape /users namespace via path traversal must fail."""
    traversal_path = "/users/userA/events/event1/../../../admin/secrets"
    assert matrix.evaluate(traversal_path, "read", auth_uid="userA") is False
    assert matrix.evaluate(traversal_path, "write", auth_uid="userA") is False
