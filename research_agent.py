"""
Composio App Research Agent
============================

For each app in apps.APPS, produces one structured row:

    {
      "name", "category", "one_liner",
      "auth_methods": [...],            # e.g. ["OAuth2"], ["API Key", "Basic"]
      "self_serve": "self_serve" | "gated" | "unclear",
      "gate_reason": str | null,        # e.g. "requires paid plan", "partner-only"
      "api_surface": "REST" | "GraphQL" | "REST+GraphQL" | "none_public" | "unclear",
      "api_breadth": "broad" | "narrow" | "unclear",
      "existing_mcp": true | false | "unclear",
      "composio_native": true | false,  # Composio already ships a toolkit for it
      "buildable_today": true | false | "partial",
      "blocker": str | null,
      "evidence_url": str,
      "notes": str,
      "confidence": "high" | "medium" | "low",
    }

How it works
------------
1. `check_composio_native()` asks Composio's own catalog (`composio.toolkits`)
   whether a toolkit already exists for the app. If it does, that's strong
   ground-truth evidence for auth scheme + "self-serve" + "buildable today" -
   Composio would not have shipped it otherwise - and we fold that into the
   verdict instead of re-deriving it from scratch.
2. For everything else, a Composio session (via the Anthropic provider) hands
   Claude real tools - Firecrawl/Apify-backed scraping toolkits, already in
   Composio's catalog - so the agent reads the actual docs page rather than
   pattern-matching on the app's name. This is the "use Composio's own SDK
   and MCP to build it" part of the brief: the research pipeline is itself a
   Composio-tooled agent.
3. Claude is forced to call a `submit_research` tool with a strict JSON
   schema, so output is structured, not prose to be re-parsed.
4. Every session is also exposed as an MCP endpoint (session.mcp.url) so the
   same pipeline can be driven by any MCP client, not just this script.

Run:
    export COMPOSIO_API_KEY=...
    export ANTHROPIC_API_KEY=...
    python research_agent.py --out apps_data.json
    python research_agent.py --sample 10 --out sample.json     # quick smoke test
    python research_agent.py --workers 8 --out apps_data.json  # full 100, parallel
"""

import argparse
import json
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from apps import APPS

RESEARCH_TOOL_SCHEMA = {
    "name": "submit_research",
    "description": "Submit the structured research result for one app.",
    "input_schema": {
        "type": "object",
        "properties": {
            "one_liner": {"type": "string", "description": "What the app does, one sentence."},
            "auth_methods": {
                "type": "array",
                "items": {"type": "string", "enum": ["OAuth2", "API Key", "Basic", "Bearer Token", "OAuth1", "Other", "None public"]},
            },
            "self_serve": {"type": "string", "enum": ["self_serve", "gated", "unclear"]},
            "gate_reason": {"type": ["string", "null"], "description": "Why it's gated, if it is. Null if self-serve."},
            "api_surface": {"type": "string", "enum": ["REST", "GraphQL", "REST+GraphQL", "none_public", "unclear"]},
            "api_breadth": {"type": "string", "enum": ["broad", "narrow", "unclear"], "description": "Roughly how many resources/endpoints are covered."},
            "existing_mcp": {"type": "string", "enum": ["yes", "no", "unclear"]},
            "buildable_today": {"type": "string", "enum": ["yes", "no", "partial"]},
            "blocker": {"type": ["string", "null"], "description": "The main blocker if not fully buildable today. Null if buildable_today is yes."},
            "evidence_url": {"type": "string", "description": "The specific docs URL you based this on."},
            "notes": {"type": "string", "description": "1-2 sentences of anything a reviewer should know (edge cases, ambiguity, what you couldn't verify)."},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        },
        "required": [
            "one_liner", "auth_methods", "self_serve", "api_surface", "api_breadth",
            "existing_mcp", "buildable_today", "evidence_url", "notes", "confidence",
        ],
    },
}

SYSTEM_PROMPT = """You are an API research analyst. You are given one app and must determine,
from PRIMARY sources only (the app's own developer docs, not blog posts or aggregators),
its auth model, whether a developer can self-serve credentials, its public API surface, and
whether it could become an agent-callable toolkit today.

Rules:
- Use your tools to actually open the docs URL you're given (and follow links from it) before
  answering. Do not answer from memory alone - docs change, and pricing/gating changes often.
- If you cannot find a public API or the docs are behind a login you cannot pass, say so plainly:
  api_surface="none_public" or self_serve="unclear", confidence="low". Do not guess to fill a field.
- "gated" means real developer credentials require: a paid/enterprise plan, admin/manual approval,
  or a partnership / contact-sales flow. A free-tier or trial dev account still counts as self_serve.
- When you are done, call submit_research exactly once with your findings. Do not answer in prose.
"""


def get_clients():
    """Lazily construct the Composio + Anthropic clients so --help works without keys set."""
    from composio import Composio
    from composio_anthropic import AnthropicProvider
    import anthropic

    composio = Composio(provider=AnthropicProvider())
    claude = anthropic.Anthropic()
    return composio, claude


def check_composio_native(composio, slug_guess: str, app_name: str):
    """
    Ask Composio's own catalog whether it already has a toolkit for this app.
    Tries the guessed slug first, then falls back to a search over
    `composio.toolkits.list()` matching on display name.
    Returns the toolkit dict (or None) plus a normalized summary of what it implies.
    """
    try:
        toolkit = composio.toolkits.get(slug_guess)
        if toolkit:
            return _summarize_native(toolkit)
    except Exception:
        pass

    try:
        catalog = composio.toolkits.list()
        items = getattr(catalog, "items", catalog)
        for tk in items:
            name = getattr(tk, "name", "") or getattr(tk, "slug", "")
            if app_name.split()[0].lower() in str(name).lower():
                return _summarize_native(tk)
    except Exception:
        pass

    return None


def _summarize_native(toolkit) -> dict:
    auth_schemes = getattr(toolkit, "auth_schemes", None) or getattr(toolkit, "authSchemes", [])
    tool_count = getattr(toolkit, "tools_count", None) or getattr(toolkit, "toolsCount", None)
    return {
        "composio_native": True,
        "auth_schemes": [str(s) for s in (auth_schemes or [])],
        "tool_count": tool_count,
    }


def research_app(composio, claude, app, model="claude-sonnet-4-6", max_turns=6):
    name, category, hint_url, slug_guess = app
    native = check_composio_native(composio, slug_guess, name)

    # Give the agent real tools: a scraping-capable Composio session
    # (Firecrawl is already in Composio's catalog, so this is Composio-on-Composio).
    session = composio.create(user_id="research-agent", toolkits=["firecrawl"])
    tools = session.tools() + [RESEARCH_TOOL_SCHEMA]

    docs_hint = hint_url if hint_url.startswith("http") else f"https://{hint_url}"
    user_prompt = (
        f"App: {name}\nCategory (assumed): {category}\nDocs hint: {docs_hint}\n\n"
        + (
            f"Note: Composio's own catalog already lists a toolkit for this app with "
            f"auth scheme(s) {native['auth_schemes']} and {native['tool_count']} tools. "
            f"Use that as a strong signal but still verify self-serve status and gating from docs.\n\n"
            if native
            else ""
        )
        + "Research this app and call submit_research with your findings."
    )

    messages = [{"role": "user", "content": user_prompt}]
    result = None

    for _ in range(max_turns):
        response = claude.messages.create(
            model=model,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            break

        tool_results = []
        for block in tool_uses:
            if block.name == "submit_research":
                result = block.input
                continue
            # Everything else is a real Composio tool call - execute it.
            try:
                output = composio.tools.execute(
                    slug=block.name, arguments=block.input, user_id="research-agent"
                )
            except Exception as e:
                output = {"error": str(e)}
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(output)[:4000]}
            )

        if result is not None:
            break
        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    row = {"name": name, "category": category, "hint_url": hint_url}
    if result:
        row.update(result)
    else:
        row.update({
            "one_liner": "", "auth_methods": [], "self_serve": "unclear",
            "gate_reason": None, "api_surface": "unclear", "api_breadth": "unclear",
            "existing_mcp": "unclear", "buildable_today": "partial",
            "blocker": "agent did not return a result within max_turns",
            "evidence_url": docs_hint, "notes": "needs manual research", "confidence": "low",
        })
    row["composio_native"] = bool(native)
    if native:
        row["composio_native_auth_schemes"] = native["auth_schemes"]
        row["composio_native_tool_count"] = native["tool_count"]
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="apps_data.json")
    parser.add_argument("--sample", type=int, default=0, help="only research the first N apps (smoke test)")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    apps = APPS[: args.sample] if args.sample else APPS
    composio, claude = get_clients()

    results = []
    errors = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(research_app, composio, claude, app): app for app in apps}
        for i, fut in enumerate(as_completed(futures), 1):
            app = futures[fut]
            try:
                row = fut.result()
                results.append(row)
                print(f"[{i}/{len(apps)}] done: {app[0]}", file=sys.stderr)
            except Exception as e:
                errors.append({"app": app[0], "error": str(e), "trace": traceback.format_exc()})
                print(f"[{i}/{len(apps)}] FAILED: {app[0]} - {e}", file=sys.stderr)

    with open(args.out, "w") as f:
        json.dump({"generated_at": time.time(), "results": results, "errors": errors}, f, indent=2)
    print(f"\nWrote {len(results)} rows ({len(errors)} errors) to {args.out}")


if __name__ == "__main__":
    main()
