from enum import Enum

class Status(str, Enum):
    VALID = "VALID"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    INVALID = "INVALID"

# Some issues are severe enough to be INVALID outright (no matching record,
# duplicate, unreadable data) rather than just "needs a human look".
HARD_FAIL_KEYWORDS = ["Duplicate", "not recorded", "No matching record"]

def decide(issues: list[str]) -> tuple[Status, list[str]]:
    if not issues:
        return Status.VALID, []
    if any(any(k in issue for k in HARD_FAIL_KEYWORDS) for issue in issues):
        return Status.INVALID, issues
    return Status.REVIEW_REQUIRED, issues