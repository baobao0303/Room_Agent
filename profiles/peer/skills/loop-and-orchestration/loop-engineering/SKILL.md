---
name: loop-engineering
description: Use when the user wants Claude Code to keep working on its own until a goal is met — a self-running loop instead of write→wait→review→re-prompt. Helps decide if a loop is even worth building, picks manual vs automatic and open vs closed, distinguishes /goal vs /loop vs routines (/schedule), and wires up a CLOSED loop with a real verification gate (Stop hook running tests, or an LLM-judge + rubric when output isn't testable) plus a turn/budget ceiling so it never spins forever. Triggers on "loop", "döngü", "loop engineering", "auto mode", "run until tests pass", "self-running / autonomous agent", "/goal", "Stop hook", "ralph wiggum".
---

# Loop Engineering

Build the system that prompts the agent **for** the user, instead of the user prompting the agent every 15 minutes.

The bottleneck in most AI-agent work is the human in the loop: prompt → Claude runs → stops → you read → prompt again. The leverage is no longer a better prompt — it's a loop that closes itself. This skill helps the user design and wire up that loop **inside Claude Code**, with a mechanical gate that can't be fooled.

## The one rule that makes a loop trustworthy

**Never let the AI verify its own "done."** Maker and checker must be different things. When the same model writes the code and judges whether it's finished, it will happily believe its own "done" — half-built code, placeholders, a non-compiling repo by morning. This is *false completeness*. The gate must be mechanical (a real test/build/lint) or, when the output genuinely isn't testable, a **separate** LLM-judge with an explicit rubric.

## Step 1 — The honesty test (run this BEFORE building anything)

A loop is not worth it for every task. Use `AskUserQuestion` to check the four conditions. If any answer is "no," say so plainly and recommend a plain prompt instead — don't build the loop just to burn tokens.

1. **Repetitive?** One-shot task → a good prompt beats a loop. A loop pays off only when the work recurs.
2. **Verification automatable?** Is there a test / build / lint / script that returns a hard pass/fail? If not, the agent grades its own homework and the gate is meaningless (unless you accept an LLM-judge, see Step 4b).
3. **Budget?** Closed loops are cheap *when built right*, but not free.
4. **Tools?** Does the agent have an isolated environment where it can run the test, read logs, and edit files?

If all four hold, continue. Otherwise, stop and recommend the simpler path.

## Step 2 — Place the task on two independent axes

People conflate these — keep them separate.

**Axis A — who closes the loop?**
- *Manual (you are the loop):* prompt → run → stop → you review → prompt again. Progress depends on your tempo; no you, no progress.
- *Automatic (Claude closes the loop):* give a goal → Claude works → a checker asks "done?" → done ⇒ stop, not done ⇒ another turn. You leave the loop.

**Axis B — is there a gate?**
- *Open loop:* "go handle it," no boundary. Powerful but expensive, surprising, and if the agent drifts off-target you won't know. Only for unlimited budgets.
- *Closed loop:* a clear goal, a control gate, and a hard stop. Cheap, safe, repeatable. Right for routine work.

**Loop engineering = Automatic + Closed.** That is the target architecture this skill builds.

## Step 3 — Pick the right Claude Code primitive (don't confuse the three)

- **`/goal "..."`** — conditional closed loop. Claude works across turns until the goal is met; after each turn a small fast model (Haiku by default) checks completion and stops when reached. The ready-made engine for "run until X."
- **`/loop`** — *not* scheduling. It re-runs a prompt in the *same open session*, either on a fixed interval (`/loop 5m ...`) or self-paced if you omit the interval. Dies when the session closes.
- **Routines (`/schedule`)** — cron in Anthropic's cloud. "Every night at 3am, run X" — runs even with your machine off. This is calendar automation, a separate concern.

For the closed-loop architecture here, the spine is **`/goal`** — and, for anything testable, the stronger **Stop hook** in Step 4.

## Step 4 — Build the gate (the heart of the system)

### 4a — Testable work (code): use a Stop hook, never an LLM

For code, the gate is a `Stop` hook that runs the real test. Claude fires it every time it tries to stop; if the test is red, the hook refuses the stop and throws Claude back in to keep solving.

- It's **un-foolable**: output is green or red, no "good enough."
- It costs **zero tokens**: verification is a plain script, not a model call.

Wire it in `.claude/settings.json` on the `Stop` event, pointing at a small script that runs the test (e.g. behind `npm test`). The hook blocks the stop by either returning **exit code 2**, or printing `{"decision": "block", "reason": "..."}`. Either way Claude can't stop while the suite is red.

Conceptual shape:

```json
{
  "hooks": {
    "Stop": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "python3 .claude/gate.py" }] }
    ]
  }
}
```

```python
# .claude/gate.py — runs the real test; exit 2 keeps Claude looping
import subprocess, sys
result = subprocess.run(["npm", "test"], capture_output=True, text=True)
if result.returncode != 0:
    print('{"decision": "block", "reason": "Tests are red. Keep fixing until green."}')
    sys.exit(2)   # block the stop
sys.exit(0)        # green → allow stop
```

### 4b — Non-testable work (a deck, prose, "does this look good?")

There is no script for taste. Here the gate is a **separate** agent with an explicit rubric (clear criteria), not the maker. Accept that this gate costs tokens. Keep the rubric concrete so the judgment is reproducible.

## Step 5 — Always add a ceiling

A gate alone isn't enough. Without a maximum, the loop either gives up too early or spins forever, burning tokens and bloating the context window with stacked memory. Always set **`max_turns` or a budget limit**. Decide this ceiling up front.

## Step 6 — Route models for cost

- **Maker (writes/edits code):** strong model (Sonnet or Opus).
- **Verification, log reading, general evaluation:** cheap model (Haiku).

Don't pay a premium model to read logs or judge. The Stop-hook gate itself is free (it's a script), which is the single biggest saving.

## Step 7 — Wire the minimal closed loop

Four parts, all native to Claude Code, no extra framework:

1. **Goal** — a concrete, testable task ("reject the signup if the password is shorter than 8 chars"). If you don't know which file holds the bug, don't force a file on the agent — say "investigate this behaviour, find the cause, fix it."
2. **Maker** — the coding agent on a strong model.
3. **Gate** — the `Stop` hook from Step 4a (zero-token, un-foolable).
4. **Bound** — `/goal "loop until tests pass"` plus a turn/budget ceiling.

## Step 8 — Prove it actually loops

Don't trust the "auto mode on" banner — prove the gate works:

1. Deliberately re-introduce the bug (e.g. a tiny `reset.js` that breaks the code).
2. Tell the agent "fix until tests pass" and take your hands off the keyboard.
3. Watch the gate catch the red test and the loop repair the code on its own until the screen goes green.

The real control is the script you wrote, not the banner.

## Why a closed loop is cheaper, not a wallet-drainer

The common fear is "a self-running loop will burn endless tokens." Built right, the opposite is true:

- **Context caching** — each turn re-reads context at ~10% cost instead of reprocessing from scratch.
- **Model routing** — heavy/verify work on cheap models, the brain on the strong one (~5× advantage).
- **Gate = zero tokens** — verification is a script, not a model call. The biggest saving.
- **Hard ceilings** — `max_turns`/budget means it never runs to infinity.

The real token monster is the **open** loop, where none of these guards exist.

## Beyond a single loop (inner → outer)

A single closed loop is an *inner loop*. Many inner loops, sharing a memory layer (records, signals, logs) and coordinated by a manager that decides what to do next and gets smarter over time, form an *outer loop*. A network of agents is only as sound as the inner loops under it — if any inner loop lacks a real mechanical gate, agents falsely sign off their own output and the errors cascade. **Get the inner-loop gate right first.**

## How to run this skill

1. Run the **honesty test** (Step 1) with `AskUserQuestion`. If it fails, recommend a plain prompt and stop.
2. Establish the target as **Automatic + Closed** (Steps 2–3).
3. Determine whether the work is **testable** and build the matching gate (Step 4a or 4b).
4. Set the **ceiling** (Step 5) and **model routing** (Step 6).
5. Wire the four parts (Step 7) and **prove it** (Step 8).

Ask the user for the missing pieces — the goal, the test command, the ceiling — rather than guessing. The whole point is a gate that can't be fooled; never substitute the agent's self-assessment for a real check.
