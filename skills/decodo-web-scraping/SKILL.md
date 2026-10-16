---
name: decodo-web-scraping
description: >-
  Scrape websites and extract structured web data with Decodo — search the web, map a
  site's URLs, crawl a whole site or section, pull product data from Amazon, Walmart, Target,
  and collect posts from Reddit, TikTok, YouTube and more. Decodo handles JavaScript rendering,
  anti-bot/CAPTCHA, proxy rotation, and geo-targeting (125M+ IPs, 195+ locations). Reach for
  this skill whenever a plain fetch is blocked or returns junk, when a page needs JS to render,
  or when the user wants search results, a list of a site's pages, many pages of one site,
  e-commerce data, SERP data, or social media data — instead of curl, requests, BeautifulSoup,
  Playwright, Puppeteer, or a hand-written crawler.
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
- Listing the pages of a site (map) or fetching many pages of one site or section (crawl).
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

The user needs a Decodo **API key** from the dashboard at <https://dashboard.decodo.com/web-data/playground>
(free account = up to 2K requests, no card). One key covers scraping, search, map and crawl.

Older plans only have a **basic auth token**. It works for `scrape`, `screenshot` and target
commands, but `search`, `map` and `crawl` need an API key and reject a basic token with exit
code `3`. `decodo whoami` prints `api key:` or `token:` so you can tell which one is set.

Prefer the environment variable — it needs no interaction and is easy to scope to a session:

```bash
export DECODO_AUTH_TOKEN='<api-key>'
```

The variable is named `DECODO_AUTH_TOKEN`, which holds an API key.

To persist it to the CLI config non-interactively:

```bash
decodo setup --token '<api-key>'   # validates, then saves to config
```

Do **not** run a bare `decodo setup` — it opens a hidden interactive prompt you cannot drive.
Credential precedence: `--token` flag → `DECODO_AUTH_TOKEN` env → saved config.

**Treat the key as a secret.** If `whoami` reports no auth, ask the user to set
`DECODO_AUTH_TOKEN` or run `decodo setup --token <api-key>`. Never `cat`, read, or print the key
from a config file (e.g. `~/.config/decodo/config.json`) to work around missing auth.

### 3. Install for repeat use (optional)

```bash
npm install -g @decodo/cli                                # any platform (recommended)
```

macOS/Linux alternative — download and inspect before running:

```bash
curl -fsSL https://decodo.github.io/cli/install.sh -o install.sh
# review install.sh before proceeding
sh install.sh && rm install.sh
```

`npx -y @decodo/cli <command>` works with zero install if you'd rather not install anything.

## Choosing a surface

1. **Shell available** (Claude Code, Cursor, Codex CLI, Gemini CLI, Windsurf, terminal) → use
   the **`decodo` CLI**. This is the default and the rest of this skill assumes it.
2. **No shell** (Claude Desktop, claude.ai, an MCP-only client) → use the hosted **MCP server**
   at `https://mcp.decodo.com/mcp` (Bearer auth with the same API key). Per-client config in
   [`references/mcp-setup.md`](references/mcp-setup.md).
3. **Neither** → call the **raw HTTP API** with `curl` — recipes in
   [`references/api-curl.md`](references/api-curl.md).

## Usage (CLI)

### Core commands

```bash
decodo scrape https://example.com                  # markdown by default
decodo scrape https://example.com --country us     # geo-target the request
decodo search "best web scraping api" | jq -r '.organic[].link'   # web search, JSON
decodo search "query" --geo de --locale de-DE --page 2           # geo, locale, next page
decodo map https://example.com --limit 100                       # site URLs, one per line
decodo screenshot https://example.com -o shot.png                # PNG must go to a file
```

`search` always returns parsed JSON (`organic`, `top_stories`, `people_also_ask`, …) and takes
only `--geo`, `--locale` and `--page`. It has no `--engine`, `--limit` or `--parse`. For a
specific engine or its full SERP, use the `google-search` or `bing-search` target (below).

### Search, map and crawl a site

`search`, `map` and `crawl` run on the Data API and need an **API key** (see Setup step 2).

**Map first.** `map` lists a site's URLs without fetching them: cheap, fast, small output.
Use it to see what exists, then either `scrape` the few pages you need or crawl a scoped
section. Don't crawl a whole site to find one page.

```bash
decodo map https://docs.example.com --limit 200 -o urls.txt
wc -l urls.txt; grep -i pricing urls.txt | head
decodo map https://example.com --select-paths "/blog/*" --exclude-paths "/blog/tag/*" --limit 100
```

**Scope every crawl.** Always pass `--limit`, and narrow with `--select-paths` /
`--exclude-paths` (repeatable) or `--max-depth`. Unscoped crawls are slow and burn requests.

| Flag (map and crawl) | Effect |
| --- | --- |
| `--limit <n>` | Max pages. Always set it |
| `--select-paths <glob>` | Only paths matching, e.g. `"/docs/*"`. Repeatable |
| `--exclude-paths <glob>` | Skip matching paths. Repeatable |
| `--sitemap include\|only\|skip` | Use the sitemap with page links, only it, or ignore it |
| `--domain-filter domain\|subdomain\|all` | Which hosts to follow |
| `--geo`, `--locale` | Geo-target the requests |
| `--max-depth <n>` | Crawl only: link depth from the start URL |
| `--max-duration <s>` | Crawl only: stop the crawl after this many seconds |
| `--content-format markdown\|html` | Crawl only: page content format |
| `--js-rendering` | Map only: render JS while discovering links |

**Start crawls async, collect later.** `decodo crawl <url>` returns at once and prints only the
crawl id. Keep working, then collect the pages with `crawl results --wait`, which polls until
the crawl finishes:

```bash
id=$(decodo crawl https://docs.example.com --select-paths "/docs/*" --limit 50)
# ... other work ...
decodo crawl status "$id"                                 # discovered/completed/failed, status
decodo crawl results "$id" --wait --progress -o pages.ndjson
decodo crawl cancel "$id"                                 # stop early; crawled pages stay readable
```

For a small crawl you'll wait on anyway, start and collect in one call:
`decodo crawl <url> --limit 20 --wait -o pages.ndjson` (the id goes to stderr).
`--wait` polls every `--poll-interval` seconds (default 5) and gives up after `--timeout`
seconds (default 3600, exit `6`); the crawl keeps running until you cancel it.
`truncated`/`cancelled` crawls print a warning; a `faulted` crawl writes its pages, then exits `7`.

**Never print crawl output into your context.** Always write it to a file with `-o`, then read
it in slices. Each NDJSON line is one page: `url`, `depth`, `status`, `content`, …

```bash
wc -l pages.ndjson                                        # how many pages
jq -r '[.status, .url] | @tsv' pages.ndjson | head -50    # page list, no content
jq -r 'select(.url | test("/pricing")) | .content' pages.ndjson | head -c 4000
jq -r 'select(.content_error) | .url' pages.ndjson        # pages that failed
decodo crawl results "$id" --no-content -o index.ndjson   # metadata only, no content
```

Don't `cat` the file, and don't `head -n` it either: one line can hold a whole page.

### Discover targets — don't guess

Target subcommands are generated from the live API schema, so **list and introspect them**
rather than memorizing them:

```bash
decodo targets                 # all targets, grouped (e.g. google-search, amazon-product, reddit-post)
decodo google-search --help    # exact flags for a target (--parse, --geo, ...)
decodo amazon-product --help
```

**Prefer a dedicated target** (`reddit-subreddit`, `amazon-product`, …) over a generic
`scrape <url>` when one exists — it returns parsed, cleaner data and avoids guesswork. Check
`decodo targets` first.

Then call a target directly:

```bash
decodo google-search "query" --parse        # structured JSON instead of raw SERP
decodo amazon-product B09H74FXNW --parse
decodo universal https://example.com         # generic target with the most flags — see --help
```

## Output handling (important for piping)

By default a command prints the first result's `content` (markdown for `scrape`, parsed
JSON for targets called with `--parse`). These modifiers apply to `scrape` and target commands.
`search`, `map` and `crawl` support a subset; check `decodo <command> --help`.

| Flag | Effect |
| --- | --- |
| `--parse` | Structured JSON for targets that support it — **only on target commands** (e.g. `google-search`), not on `scrape`/`search`. Check `--help`. |
| `--full` | Emit the full API response envelope (status, headers, task id, all results) |
| `--format ndjson` | One JSON object per result — best for streaming into `jq` |
| `--pretty` | Indented JSON |
| `-o, --output <path>` | Write to a file instead of stdout. Screenshots always write to a file (never stdout); `-o` sets the path, otherwise it defaults to `<host>.png` |
| `-v, --verbose` | Debug logs to **stderr** (stdout stays clean data) |

The parsed JSON shape is target-specific. Pipe to `jq 'keys'` (then drill down, e.g.
`jq '.results | keys'`) to discover the structure before writing a deeper query.

**Keep context small.** Pipe straight to `jq` and select only the fields you need; make one
request and extract from it. Don't dump raw, `--pretty`, or `--full` payloads just to "inspect"
— use `jq 'keys'`. `--full` includes the response envelope (large headers/cookies), so use it
only when you actually need status/headers.

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
| 3 | Auth error | Key missing/invalid, or a basic token on `search`/`map`/`crawl` → redo **Setup step 2** with an API key |
| 4 | Validation error | Fix the argument/flag the message names |
| 5 | Rate limited | Back off and retry; reduce concurrency |
| 6 | Timeout | Retry with backoff |
| 7 | Network/server error, or a `faulted` crawl | Retry with backoff |

## Search, map and crawl over MCP

The hosted MCP server has the same Data API tools; they also need an API key, not a basic token.

- `search` — web search; `limit` caps organic results (10 by default).
- `map` — site URLs as a JSON list; `limit` defaults to 10, so set it and narrow with
  `selectPaths` / `excludePaths`. Then `scrape_as_markdown` only the pages you need.
- Crawl is async, in four tools:
  1. `crawl_start` with `url`, a `limit` and path filters → returns `crawl_id` at once.
  2. `crawl_status` with `crawlId` → poll every 10–30 s, doing other work in between,
     until `status` is no longer `pending`.
  3. `crawl_results` with `crawlId` → about 50 KB per call. Pass `nextCursor` back as `cursor`
     until it is missing. A long page is split across calls; `contentPart` gives the range.
  4. `crawl_cancel` with `crawlId` → stop early; pages crawled so far stay readable.

Read one `crawl_results` page at a time and keep only what the task needs, rather than
collecting every page before you start.

## Raw API fallback (no CLI, no MCP)

```bash
curl -s https://data.decodo.com/v1/scrape \
  -H "Authorization: Bearer $DECODO_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-integration: agent-skills" \
  -d '{"target":"universal","url":"https://example.com","markdown":true}'
```

The key is the same API key from the dashboard, sent as a Bearer token. More recipes (parsed SERP,
screenshots, target names, response shape) in [`references/api-curl.md`](references/api-curl.md).
Prefer the CLI or MCP when available.

## Links

- CLI: <https://github.com/Decodo/cli> · `@decodo/cli` on npm
- MCP server: <https://github.com/Decodo/mcp-server> · hosted at `https://mcp.decodo.com/mcp`
- Dashboard / API key / free tier: <https://dashboard.decodo.com>
