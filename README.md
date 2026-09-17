


# Composio App Research Agent
The research agent which can dive deep into website applications for data researching and analysis.
Researches and produces a structured,
evidence-linked verdict per app (auth model, self-serve vs gated, API
surface, buildability). Built *with* Composio: the
research agent's own tools and an MCP endpoint.

## Setup

```bash
pip install -r requirements.txt
export COMPOSIO_API_KEY=...      # from https://app.composio.dev
export ANTHROPIC_API_KEY=...     # from https://console.anthropic.com
```

## Run the research pass

```bash
# smoke test on 10 apps 
python research_agent.py --sample 10 --out sample.json

# full run, 8 apps in parallel
python research_agent.py --workers 8 --out apps_data.json
```

Each app goes through two steps (see `research_agent.py` for the full
logic):

1. **Composio-native check** - is there already a Composio toolkit for
   this app? If so, its auth scheme(s) and tool count are strong
   ground-truth evidence, folded into the prompt so the agent doesn't
   re-derive what's already known.
2. **Agent research pass** - a Composio session (Anthropic provider) gives
   Claude a real docs-scraping tool. Claude reads the actual docs page(s)
   and is forced to call `submit_research` with a strict JSON schema - no
   free-text answers to re-parse.

## Verify the results

Two independent checks, not one:

```bash
# 1. Generate a hand-check template for a random sample of apps
python verify.py --data apps_data.json --sample 15 --make-template

# ... open human_review.csv, click through each evidence_url,
#     fill in correct_value + is_correct(y/n) ...

# 2. Score pass-1 accuracy against your hand-checks
python verify.py --data apps_data.json --human human_review.csv

# 3.  blind second pass: re-derive the same
#    sample from a fresh session with no memory of pass 1, and see where
#    the two independent runs disagree
python verify.py --data apps_data.json --sample 15 --blind-second-pass
```

`verify.py` writes `verification_report.json` with:
- `human_gold_check`: pass-1 accuracy against your manual checks, overall
  and per field.
- `blind_second_pass`: agreement rate between two independent agent runs,
  and the specific apps/fields where they disagreed (those are the ones
  that need a third, human-adjudicated pass before you trust them).

Report the **human-gold accuracy number**, not the agent's self-reported
`confidence` field, on the case study page - that's the honest one.

## Where a human is still needed

- Anything the agent marks `confidence: "low"` or `self_serve: "unclear"` -
  usually apps whose docs are thin, gated behind a sales call, or where
  pricing pages contradict the API docs.
- Any field flagged by the blind second pass as a disagreement.
- Apps with no public docs at all (some in category 9 and 10 of the list)
  - these need a plain web search for a partner/API-access page rather
    than a docs crawl.

## Files

| File | Purpose |
|---|---|
| `apps.py` | The list as structured data |
| `research_agent.py` | The research agent (Composio + Claude) |
| `verify.py` | Verification loop: blind second pass + human gold check |
| `apps_data.json` | Output of `research_agent.py` (generated) |
| `human_review.csv` | Your hand-checked sample (generated template, then filled in by you) |
| `verification_report.json` | Output of `verify.py` (generated) |
| `case_study.html` | The reviewer-facing page - reads the same shape of data as `apps_data.json` |
