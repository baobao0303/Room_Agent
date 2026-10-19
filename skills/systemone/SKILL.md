---
name: systemone
description: "Use when the user asks to score, rate, triage, or prioritise a situation with 9router systemone. Returns confidence 0-1 for predefined questions — not chat text."
---

# systemone — structured scoring via 9router

Scores a situation against **predefined** questions and returns a confidence
`0-1` per question. It does NOT return prose, does not stream, and has no tools.

## When this is the wrong tool

If the user wants a reply written, code edited, files read, or a command run,
this endpoint cannot do it — use the normal chat model. Reach for systemone only
when the goal is a **number** (triage, urgency, confidence, priority).

## Usage

```bash
python3 ~/.paseo/skills/systemone.py "<situation text>" \
  -q urgent="Does this request require urgent attention?" \
  -q angry="Is the customer angry?"
```

Output:

```
model: jev-1.13-free
  urgent         0.950
  angry          0.930
usage: 304 in / 37 out   cost: 0
```

Use `-m <model>` to switch models. Env overrides: `SYSTEMONE_URL`,
`SYSTEMONE_KEY`, `SYSTEMONE_MODEL`.

## Hard constraints

- **Only `type: "noul"` works.** Every other type (`bool`, `number`, `text`,
  `choice`, `score`, `enum`, `scale`, `label`) returns 400 or 422.
- **Use the `-free` model.** `oc/jev-1.13` returns 401 rate-limited;
  `ocz/jev-1.13` returns 402 insufficient funds. `oc/jev-1.13-free` and
  `ocz/jev-1.13-free` both work.
- **`stream`, `tools`, `system`, and `messages` are all rejected** with
  400 `Invalid request`. Both `state` and `questions` are required fields.
- No question history: each call is stateless, so re-send full context in `state`.

## Reading the score

Scores are model confidence, not truth. `0.9` means the model is confident, not
that the situation is 90% urgent. Two independent questions scored together are
cheaper and more stable than one repeated call — a single call answers many
questions, and repeat-call variance is high (same input has been observed at 0.43
and 0.95 on different questions).
