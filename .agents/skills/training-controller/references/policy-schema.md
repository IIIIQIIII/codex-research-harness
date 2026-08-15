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

```json
{
  "current_step": 12000,
  "reviewed_gates": [],
  "consecutive_bad_reviews": 0,
  "soft_stop_requested": false,
  "hard_stop": {
    "triggered": false,
    "reason": ""
  }
}
```

Fields:

- `current_step`: latest verified training step.
- `reviewed_gates`: gates already evaluated and recorded.
- `consecutive_bad_reviews`: number of consecutive review gates that met the precommitted bad-review criterion.
- `soft_stop_requested`: whether the scientific/economic policy currently proposes stopping the healthy run.
- `hard_stop.triggered`: whether a precommitted hard-failure condition is currently satisfied.
- `hard_stop.reason`: factual reason for the hard stop.

## Possible actions

- `STOP_NOW_HARD`: hard failure overrides all other states.
- `CONTINUE_PROTECTED`: minimum evidence horizon has not been reached.
- `REVIEW_REQUIRED`: an eligible unreviewed gate has been reached.
- `STOP_ALLOWED_SOFT`: a review gate is active and soft-stop hysteresis requirements are satisfied.
- `CONTINUE_TO_NEXT_GATE`: a soft stop is desired but no eligible gate currently authorizes it.
- `CONTINUE_OBSERVE`: healthy run; continue observing.
- `COMPLETE`: completion horizon has been reached and no review gate remains pending.

## Integration guidance

A launcher can choose to enforce these actions, but keep the policy check separate from process control. This separation makes it possible to test whether an intervention was authorized without granting the reasoning agent direct unrestricted process-kill authority.
