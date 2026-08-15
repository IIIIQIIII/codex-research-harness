#!/usr/bin/env python3
"""Deterministic intervention-authority checker for long training runs.

This tool is intentionally side-effect free. It never launches, kills, signals,
checkpoints, or edits a training process. It only evaluates policy + state.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class PolicyError(ValueError):
    pass


def _as_nonnegative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PolicyError(f"{name} must be a non-negative integer")
    return value


def validate_policy(policy: dict[str, Any]) -> None:
    minimum = _as_nonnegative_int(policy.get("minimum_evidence_step"), "minimum_evidence_step")

    gates = policy.get("review_gates")
    if not isinstance(gates, list) or not gates:
        raise PolicyError("review_gates must be a non-empty list")
    parsed_gates = [_as_nonnegative_int(g, "review_gates[]") for g in gates]
    if parsed_gates != sorted(set(parsed_gates)):
        raise PolicyError("review_gates must be strictly increasing and unique")
    if parsed_gates[0] < minimum:
        raise PolicyError("first review gate cannot precede minimum_evidence_step")

    completion = policy.get("completion_step")
    if completion is not None:
        completion = _as_nonnegative_int(completion, "completion_step")
        if completion < parsed_gates[-1]:
            raise PolicyError("completion_step cannot precede the final review gate")

    soft = policy.get("soft_stop", {})
    if not isinstance(soft, dict):
        raise PolicyError("soft_stop must be an object")
    required = _as_nonnegative_int(
        soft.get("required_consecutive_bad_reviews", 1),
        "soft_stop.required_consecutive_bad_reviews",
    )
    if required < 1:
        raise PolicyError("required_consecutive_bad_reviews must be at least 1")


def validate_state(state: dict[str, Any], policy: dict[str, Any]) -> None:
    _as_nonnegative_int(state.get("current_step"), "current_step")
    _as_nonnegative_int(state.get("consecutive_bad_reviews", 0), "consecutive_bad_reviews")

    reviewed = state.get("reviewed_gates", [])
    if not isinstance(reviewed, list):
        raise PolicyError("reviewed_gates must be a list")
    reviewed_set = {_as_nonnegative_int(g, "reviewed_gates[]") for g in reviewed}
    unknown = reviewed_set.difference(policy["review_gates"])
    if unknown:
        raise PolicyError(f"reviewed_gates contains values not present in policy: {sorted(unknown)}")

    if not isinstance(state.get("soft_stop_requested", False), bool):
        raise PolicyError("soft_stop_requested must be boolean")

    hard = state.get("hard_stop", {})
    if not isinstance(hard, dict):
        raise PolicyError("hard_stop must be an object")
    if not isinstance(hard.get("triggered", False), bool):
        raise PolicyError("hard_stop.triggered must be boolean")
    reason = hard.get("reason", "")
    if reason is not None and not isinstance(reason, str):
        raise PolicyError("hard_stop.reason must be a string")


def evaluate(policy: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    validate_policy(policy)
    validate_state(state, policy)

    current = state["current_step"]
    reviewed = set(state.get("reviewed_gates", []))
    hard = state.get("hard_stop", {})

    if hard.get("triggered", False):
        return {
            "action": "STOP_NOW_HARD",
            "reason": hard.get("reason") or "precommitted hard-stop condition triggered",
            "current_step": current,
        }

    minimum = policy["minimum_evidence_step"]
    gates = policy["review_gates"]

    if current < minimum:
        return {
            "action": "CONTINUE_PROTECTED",
            "reason": "minimum evidence horizon has not been reached",
            "current_step": current,
            "minimum_evidence_step": minimum,
            "next_review_gate": gates[0],
        }

    pending_reached = [g for g in gates if g <= current and g not in reviewed]
    if pending_reached:
        gate = min(pending_reached)
        required = policy.get("soft_stop", {}).get("required_consecutive_bad_reviews", 1)
        bad_reviews = state.get("consecutive_bad_reviews", 0)
        soft_requested = state.get("soft_stop_requested", False)

        if soft_requested and bad_reviews >= required:
            return {
                "action": "STOP_ALLOWED_SOFT",
                "reason": "eligible review gate reached and soft-stop persistence requirement satisfied",
                "current_step": current,
                "review_gate": gate,
                "consecutive_bad_reviews": bad_reviews,
                "required_consecutive_bad_reviews": required,
            }

        return {
            "action": "REVIEW_REQUIRED",
            "reason": "an unreviewed review gate has been reached",
            "current_step": current,
            "review_gate": gate,
            "soft_stop_requested": soft_requested,
            "consecutive_bad_reviews": bad_reviews,
            "required_consecutive_bad_reviews": required,
        }

    completion = policy.get("completion_step")
    if completion is not None and current >= completion:
        return {
            "action": "COMPLETE",
            "reason": "planned completion horizon reached and no review gate remains pending",
            "current_step": current,
            "completion_step": completion,
        }

    future_gates = [g for g in gates if g > current]
    next_gate = min(future_gates) if future_gates else None

    if state.get("soft_stop_requested", False):
        return {
            "action": "CONTINUE_TO_NEXT_GATE",
            "reason": "soft stop is requested but no eligible review gate currently authorizes it",
            "current_step": current,
            "next_review_gate": next_gate,
        }

    return {
        "action": "CONTINUE_OBSERVE",
        "reason": "healthy run between review gates",
        "current_step": current,
        "next_review_gate": next_gate,
    }


def load_json(path: str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise PolicyError(f"{path} must contain a JSON object")
    return data


def self_test() -> None:
    policy = {
        "minimum_evidence_step": 20,
        "review_gates": [20, 40, 60],
        "completion_step": 60,
        "soft_stop": {"required_consecutive_bad_reviews": 2},
    }

    cases = [
        (
            "hard stop overrides protected window",
            {
                "current_step": 5,
                "reviewed_gates": [],
                "consecutive_bad_reviews": 0,
                "soft_stop_requested": False,
                "hard_stop": {"triggered": True, "reason": "persistent NaN"},
            },
            "STOP_NOW_HARD",
        ),
        (
            "protected window blocks soft stop",
            {
                "current_step": 10,
                "reviewed_gates": [],
                "consecutive_bad_reviews": 3,
                "soft_stop_requested": True,
                "hard_stop": {"triggered": False, "reason": ""},
            },
            "CONTINUE_PROTECTED",
        ),
        (
            "reached gate requires review",
            {
                "current_step": 20,
                "reviewed_gates": [],
                "consecutive_bad_reviews": 1,
                "soft_stop_requested": True,
                "hard_stop": {"triggered": False, "reason": ""},
            },
            "REVIEW_REQUIRED",
        ),
        (
            "soft stop allowed only at gate with hysteresis",
            {
                "current_step": 40,
                "reviewed_gates": [20],
                "consecutive_bad_reviews": 2,
                "soft_stop_requested": True,
                "hard_stop": {"triggered": False, "reason": ""},
            },
            "STOP_ALLOWED_SOFT",
        ),
        (
            "between gates soft stop must wait",
            {
                "current_step": 30,
                "reviewed_gates": [20],
                "consecutive_bad_reviews": 2,
                "soft_stop_requested": True,
                "hard_stop": {"triggered": False, "reason": ""},
            },
            "CONTINUE_TO_NEXT_GATE",
        ),
        (
            "completion waits for final review",
            {
                "current_step": 60,
                "reviewed_gates": [20, 40],
                "consecutive_bad_reviews": 0,
                "soft_stop_requested": False,
                "hard_stop": {"triggered": False, "reason": ""},
            },
            "REVIEW_REQUIRED",
        ),
        (
            "complete after final review",
            {
                "current_step": 60,
                "reviewed_gates": [20, 40, 60],
                "consecutive_bad_reviews": 0,
                "soft_stop_requested": False,
                "hard_stop": {"triggered": False, "reason": ""},
            },
            "COMPLETE",
        ),
    ]

    for name, state, expected in cases:
        actual = evaluate(policy, state)["action"]
        assert actual == expected, f"{name}: expected {expected}, got {actual}"

    print(f"ok: {len(cases)} trainctl policy checks passed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    evaluate_parser = sub.add_parser("evaluate", help="evaluate intervention authority")
    evaluate_parser.add_argument("--policy", required=True, help="path to policy JSON")
    evaluate_parser.add_argument("--state", required=True, help="path to state JSON")
    evaluate_parser.add_argument("--pretty", action="store_true", help="pretty-print JSON")

    sub.add_parser("self-test", help="run built-in policy checks")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "self-test":
            self_test()
            return 0

        policy = load_json(args.policy)
        state = load_json(args.state)
        result = evaluate(policy, state)
        if args.pretty:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(json.dumps(result, separators=(",", ":"), sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, PolicyError, AssertionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
