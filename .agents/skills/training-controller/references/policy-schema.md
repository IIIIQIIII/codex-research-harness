# `trainctl.py` policy and state schema

`trainctl.py` is a deterministic authorization helper. It is deliberately not a trainer lifecycle manager.

## Policy JSON

```json
{
  "minimum_evidence_step": 20000,
  "review_gates": [20000, 40000, 60000, 80000],
  "completion_step": 80000,
  "soft_stop": {
    "required_consecutive_bad_reviews": 2
  }
}
```

Fields:

- `minimum_evidence_step`: before this step, healthy-run soft stopping is prohibited.
- `review_gates`: monotonically increasing steps at which a review is allowed or required.
- `completion_step`: optional planned completion step.
- `soft_stop.required_consecutive_bad_reviews`: persistence requirement before a soft stop can be authorized at a review gate.

## State JSON

Between review gates:

```json
{
  "current_step": 30000,
  "reviewed_gates": [20000],
  "consecutive_bad_reviews": 1,
  "active_review": null,
  "hard_stop": {
    "triggered": false,
    "reason": ""
  }
}
```

While evaluating the 40000-step review gate:

```json
{
  "current_step": 40000,
  "reviewed_gates": [20000],
  "consecutive_bad_reviews": 1,
  "active_review": {
    "gate": 40000,
    "evaluated": true,
    "bad": true,
    "soft_stop_requested": true
  },
  "hard_stop": {
    "triggered": false,
    "reason": ""
  }
}
```

Fields:

- `current_step`: latest verified training step.
- `reviewed_gates`: review gates already evaluated **and finalized**. The currently active gate must not appear here yet.
- `consecutive_bad_reviews`: count of consecutive bad reviews among finalized gates only.
- `active_review`: null between gates; an object while the earliest reached unfinalized gate is being reviewed.
- `active_review.gate`: the gate currently under review. It must equal the earliest reached gate not in `reviewed_gates`.
- `active_review.evaluated`: whether the gate has actually been evaluated against the precommitted criterion.
- `active_review.bad`: the result of that criterion for this gate.
- `active_review.soft_stop_requested`: whether this evaluated gate proposes a soft stop under the run policy.
- `hard_stop.triggered`: whether a precommitted hard-failure condition is currently satisfied.
- `hard_stop.reason`: factual reason for the hard stop.

## Two-phase review protocol

Review is deliberately split from finalization so a gate cannot be simultaneously "already reviewed" and "not yet reviewed."

1. At a reached gate with no `active_review`, `trainctl.py` returns `REVIEW_REQUIRED`.
2. Evaluate the gate against the precommitted criterion and populate `active_review`.
3. Call `trainctl.py` again.
4. It returns either:
   - `STOP_ALLOWED_SOFT`, if the evaluated gate plus prior finalized bad reviews satisfies the persistence rule; or
   - `FINALIZE_REVIEW_CONTINUE`, if the run should continue.
5. Before continuing past the gate, apply the returned `finalize_review` payload: add the gate to `reviewed_gates`, set `consecutive_bad_reviews`, and clear `active_review`.

If a soft stop is authorized, record/finalize the review in durable experiment state before actuating the stop when practical.

## Possible actions

- `STOP_NOW_HARD`: hard failure overrides all other states.
- `CONTINUE_PROTECTED`: minimum evidence horizon has not been reached.
- `REVIEW_REQUIRED`: an eligible unfinalized gate has been reached and needs evaluation.
- `STOP_ALLOWED_SOFT`: the active evaluated review satisfies the precommitted soft-stop hysteresis rule.
- `FINALIZE_REVIEW_CONTINUE`: the active review is evaluated, does not authorize stopping, and must be finalized before continuing.
- `CONTINUE_OBSERVE`: healthy run between finalized review gates.
- `COMPLETE`: completion horizon has been reached and no review gate remains pending.

## Integration guidance

A launcher can choose to enforce these actions, but keep the policy check separate from process control. This separation makes it possible to test whether an intervention was authorized without granting the reasoning agent direct unrestricted process-kill authority.

Do not mutate `reviewed_gates` before the current gate's decision is made. The explicit `active_review` phase is the source of truth for an in-progress gate evaluation.
