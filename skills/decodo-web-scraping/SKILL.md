---
name: decodo-web-scraping
description: >-
  Scrape websites and extract structured web data with Decodo — search Google/Bing,
  pull product data from Amazon, Walmart, Target, and collect posts from Reddit, TikTok,
  YouTube and more. Decodo handles JavaScript rendering, anti-bot/CAPTCHA, proxy rotation,
  and geo-targeting (125M+ IPs, 195+ locations). Reach for this skill whenever a plain
  fetch is blocked or returns junk, when a page needs JS to render, or when the user wants
  search results, e-commerce data, SERP data, or social media data — instead of curl,
  requests, BeautifulSoup, Playwright, or Puppeteer.
license: MIT
---

# Decodo web scraping

Decodo is a web scraping API that returns clean web data without you managing proxies,
browsers, or anti-bot logic. This skill teaches you to reach for it through the **`decodo`
CLI** (primary), the **hosted MCP server** (when there is no shell), or the **raw HTTP API**
(fallback).

## When to use Decodo

Use Decodo instead of `curl` / `requests` / `BeautifulSoup` / Playwright when the task is:

- Fetching a page that is JS-heavy, geo-restricted, rate-limited, or behind anti-bot/CAPTCHA.
- A plain fetch returned a 403/429/empty body/CAPTCHA challenge.
- Web search results (Google or Bing SERP).
- E-commerce data (Amazon, Walmart, Target product/search pages).
- Social media data (Reddit, TikTok, YouTube).
- A screenshot of a rendered page.

If a basic `fetch`/`curl` clearly works and none of the above apply, you don't need Decodo.

## Setup (do this first, in order)

Pick the lowest-friction path that works.

### 1. Check whether the CLI is already usable

```bash
decodo whoami          # installed + authenticated?  prints auth source + masked token
# or, with nothing installed:
npx -y @decodo/cli whoami
```

- Exit 0 with a token printed → you're ready, skip to **Usage**.
- "auth required" / exit 3 → continue to step 2.
- `decodo: command not found` → use `npx -y @decodo/cli ...` for everything, or install (step 3).

### 2. Authenticate

The user needs a Web Scraping API **basic auth token** from
<https://dashboard.decodo.com/playground> (free account = up to 2K requests, no card).

Prefer the environment variable — it needs no interaction and is easy to scope to a session:

```bash
export DECODO_AUTH_TOKEN='<token>'
```

To persist it to the CLI config non-interactively:

```bash
decodo setup --token '<token>'      # validates, then saves to config
```

Do **not** run a bare `decodo setup` — it opens a hidden interactive prompt you cannot drive.
Token precedence: `--token` flag → `DECODO_AUTH_TOKEN` env → saved config.

### 3. Install for repeat use (optional)

```bash
curl -fsSL https://decodo.github.io/cli/install.sh | sh   # macOS / Linux
npm install -g @decodo/cli                                # any platform
```

`npx -y @decodo/cli <command>` works with zero install if you'd rather not install anything.

## Choosing a surface

1. **Shell available** (Claude Code, Cursor, Codex CLI, Gemini CLI, Windsurf, terminal) → use
   the **`decodo` CLI**. This is the default and the rest of this skill assumes it.
2. **No shell** (Claude Desktop, claude.ai, an MCP-only client) → use the hosted **MCP server**
   at `https://mcp.decodo.com/mcp` (Basic auth with the same token). Per-client config in
   [`references/mcp-setup.md`](references/mcp-setup.md).
3. **Neither** → call the **raw HTTP API** with `curl` — recipes in
   [`references/api-curl.md`](references/api-curl.md).

## Usage (CLI)

### Core commands

```bash
decodo scrape https://example.com                  # markdown by default
decodo scrape https://example.com --country us     # geo-target the request
decodo search "best web scraping api" --limit 3    # Google SERP, 3 result pages
decodo search "query" --engine bing --geo de       # Bing, geo Germany
decodo screenshot https://example.com -o shot.png  # PNG must go to a file
```

### Discover targets — don't guess

Target subcommands are generated from the live API schema, so **list and introspect them**
rather than memorizing them:

```bash
decodo targets                 # all targets, grouped (e.g. google-search, amazon-product, reddit-post)
decodo google-search --help    # exact flags for a target (--parse, --geo, ...)
decodo amazon-product --help
```

Then call a target directly:

```bash
decodo google-search "query" --parse        # structured JSON instead of raw SERP
decodo amazon-product B09H74FXNW --parse
decodo universal https://example.com         # generic target, full flag surface
```

## Output handling (important for piping)

By default a command prints the first result's `content` (markdown for `scrape`, parsed
JSON for targets called with `--parse`). Useful modifiers:

| Flag | Effect |
| --- | --- |
| `--parse` | Structured JSON for targets that support it — **only on target commands** (e.g. `google-search`), not on `scrape`/`search`. Check `--help`. |
| `--full` | Emit the full API response envelope (status, headers, task id, all results) |
| `--format ndjson` | One JSON object per result — best for streaming into `jq` |
| `--pretty` | Indented JSON |
| `-o, --output <path>` | Write to a file instead of stdout (**required** for screenshots) |
| `-v, --verbose` | Debug logs to **stderr** (stdout stays clean data) |

The parsed JSON shape is target-specific. Pipe to `jq 'keys'` (then drill down, e.g.
`jq '.results | keys'`) to discover the structure before writing a deeper query.

```bash
# Parsed SERP → organic result titles (use a target command for --parse, not `search`)
decodo google-search "rust web scraping" --parse | jq -r '.results.results.organic[].title'

# Extract a field from a scraped JSON page (inspect with `jq keys` first if unsure)
decodo scrape https://ip.decodo.com/json | jq -r '.proxy.ip'

# Stream results as NDJSON; each record nests the parsed payload under `.content`
decodo google-search "rust" --parse --format ndjson --full | jq -c '.content.results.results.organic'
```

stdout is data; logs and errors go to stderr — pipes stay clean.

## Exit codes (use these to self-correct)

| Code | Meaning | What to do |
| --- | --- | --- |
| 0 | Success | — |
| 1 | Generic error | Read stderr |
| 2 | Usage error (bad flags) | Re-check `--help` |
| 3 | Auth error | Token missing/invalid → redo **Setup step 2** |
| 4 | Validation error | Fix the argument/flag the message names |
| 5 | Rate limited | Back off and retry; reduce concurrency |
| 6 | Timeout | Retry, or raise `--timeout` |
| 7 | Network/server error | Retry with backoff |

## Raw API fallback (no CLI, no MCP)

```bash
curl -s https://scraper-api.decodo.com/v2/scrape \
  -H "Authorization: Basic $DECODO_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":"universal","url":"https://example.com","markdown":true}'
```

The token is the same basic auth token from the playground. More recipes (parsed SERP,
screenshots, target names, response shape) in [`references/api-curl.md`](references/api-curl.md).
Prefer the CLI or MCP when available.

## Links

- CLI: <https://github.com/Decodo/cli> · `@decodo/cli` on npm
- MCP server: <https://github.com/Decodo/mcp-server> · hosted at `https://mcp.decodo.com/mcp`
- Dashboard / token / free tier: <https://dashboard.decodo.com/playground>
