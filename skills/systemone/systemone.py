#!/usr/bin/env python3
"""
Client for 9router's /v1/systemone structured-classification endpoint.

Returns confidence SCORES for predefined questions, not chat text.
Verified: only question type "noul" is supported. No streaming, no tools.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

ENDPOINT = os.environ.get("SYSTEMONE_URL", "http://100.124.36.46:20128/v1/systemone")
API_KEY = os.environ.get("SYSTEMONE_KEY", "")
DEFAULT_MODEL = os.environ.get("SYSTEMONE_MODEL", "oc/jev-1.13-free")


def call(state, questions, model=DEFAULT_MODEL, timeout=45, retries=3):
    """questions: {"name": {"type": "noul", "instructions": "..."}}"""
    payload = {"model": model, "state": state, "questions": questions}
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + API_KEY,
        },
        method="POST",
    )
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            last = "HTTP %s: %s" % (e.code, detail)
            # 402/401 are upstream account problems - retrying will not help soon
            if e.code in (400, 401, 402):
                break
        except Exception as e:
            last = str(e)
        if attempt < retries - 1:
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("systemone failed after %d tries: %s" % (retries, last))


def main():
    import argparse

    p = argparse.ArgumentParser(description="Score a situation against predefined questions.")
    p.add_argument("state", help="the situation text to analyse")
    p.add_argument("-q", "--question", action="append", default=[], metavar="NAME=QUESTION",
                   help="repeatable; e.g. -q urgent='Is this urgent?'")
    p.add_argument("-m", "--model", default=DEFAULT_MODEL)
    args = p.parse_args()

    questions = {}
    for item in args.question:
        if "=" not in item:
            sys.exit("bad --question %r (need NAME=QUESTION)" % item)
        name, text = item.split("=", 1)
        questions[name.strip()] = {"type": "noul", "instructions": text.strip()}
    if not questions:
        questions["relevance"] = {"type": "noul", "instructions": "How relevant is this to support?"}

    try:
        out = call(args.state, questions, model=args.model)
    except Exception as e:
        sys.exit(str(e))

    print("model: %s" % out.get("model"))
    for name, ans in (out.get("answers") or {}).items():
        print("  %-14s %.3f" % (name, ans.get("noul", float("nan"))))
    usage = out.get("usage") or {}
    print("usage: %s in / %s out   cost: %s" % (
        usage.get("input_tokens"), usage.get("output_tokens"), out.get("cost")))


if __name__ == "__main__":
    main()
