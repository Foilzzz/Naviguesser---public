# THE CHAIN RULE — the register's integrity rule, stated once

Single rule source: `SCORER/f1_daily_guidance.py` (the pinned emitter), functions
`canon`, `sha`, `_line_digest`, `register_head`, `append_register`, `verify_register`.
This document restates them so a reviewer can implement the check independently
(~20 lines). It never redefines them; where words and code differ, the pinned code
is the rule and the difference is a finding.

## The rule

- `canon(obj)` = `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`
- `sha(b)` = SHA-256 hex of bytes.
- Each register line is one JSON object: `{"guidance": {...}, "pin_utc": str, "pin_valid_on_time": bool, "prev_digest": str}`.
- `guidance.sha256` = `sha(canon(guidance))` computed with the `sha256` field itself **excluded** from the object.
- `prev_digest` of line *i* = `sha(line_{i-1})` over the **raw line text** with the trailing newline stripped (`line.rstrip("\n").encode("utf-8")`).
- Genesis: the first line's `prev_digest` = `"0" * 64`.
- `pin_valid_on_time` = `pin_utc < window_open`, stored at emission; verification recomputes it.

## What tampering looks like

- Editing a line's guidance content → that line's `guidance sha256 mismatch`.
- Editing a line's `prev_digest`, or inserting/deleting/reordering lines → the **next** line's `prev_digest mismatch` (a tampered link surfaces at the following link — this is expected, not a bug in the checker).
- A line that no longer parses as JSON → named `unparseable` finding. `reproduce.py` and the emitter both report this by name; neither exits by traceback, because a traceback reads as a refusal to a caller watching only the exit code.

## Timing rule (checked with the chain)

Every entry's `pin_utc` must precede its `guidance.window_open`, and
`window_open = issued_utc + 1 h` exactly (the pinned emission lag, §4 of the
trial pre-registration). A late pin is a finding, not an edit.
