---
name: decodo-price-monitoring
description: >-
  Track and compare product prices across Amazon, Walmart, Target, and Google Shopping with
  Decodo — check a current price, find the cheapest seller, or watch a product for price drops
  over time. A workflow on top of the Decodo CLI, which handles JS rendering, anti-bot, and
  geo/currency. Reach for this when the user wants to monitor or compare prices, detect a
  discount or price drop, or build a price-tracking log — instead of scraping retail pages by
  hand with curl, requests, or Playwright.
license: MIT
---

# Price monitoring with Decodo

A workflow for pricing tasks, built on the Decodo CLI: get a current price, compare across
retailers, and track prices over time to catch drops. It assumes the `decodo` CLI is set up —
for installation/auth, see the **decodo-web-scraping** skill.

## When to use

- "What does product X cost right now?"
- "Compare the price of X across retailers / find the cheapest."
- "Tell me if X drops below $Y" / "track this price over time."
- Building a price log, deal alert, or competitive pricing report.

## Prerequisites

This builds on the `decodo` CLI. Quick check:

```bash
decodo whoami    # or: npx -y @decodo/cli whoami
```

If it isn't installed or authenticated, set it up first via the **decodo-web-scraping** skill
(`npx @decodo/cli`, then `DECODO_AUTH_TOKEN` / `decodo setup --token`). Everything below assumes
the CLI works.

## Pricing targets

| Need | Targets |
| --- | --- |
| Price for a known product (ID/URL) | `amazon-pricing` / `amazon-product` (ASIN), `walmart-product`, `target-product`, or generic `ecommerce` by URL |
| Find the product first (keyword) | `amazon-search`, `walmart-search`, `target-search` |
| Compare many sellers in one call | `google-shopping-search` |

Run `decodo targets` for the full list and `decodo <target> --help` for flags — note `--parse`
(structured JSON), `--geo` (storefront/locale), and `--currency` (Amazon).

## 1. Get a current price

Use a parse-enabled target with `--parse`. Price field paths are target-specific — inspect with
`jq 'keys'` if unsure. Verified examples:

```bash
# Amazon by ASIN — price lives at .results.pricing[].price
decodo amazon-pricing B09H74FXNW --parse | jq -r '.results.pricing[].price'

# Cross-retailer via Google Shopping — sellers + prices under .results.results.organic[]
decodo google-shopping-search "logitech mx master 3s" --parse \
  | jq -r '.results.results.organic[] | "\(.price_str)\t\(.title)"'
```

## 2. Find the cheapest seller

Show the lowest listings with merchant + title and **let the user/agent judge** — don't blindly
take the global minimum. Google Shopping results mix in accessories (skins, cases, grips), used
items, and variants, so the cheapest row is often *not* the product (e.g. an $18.99 "Skins &
Wraps" outranking the $36 mouse).

```bash
decodo google-shopping-search "logitech mx master 3s" --parse \
  | jq -r '[.results.results.organic[]] | sort_by(.price) | .[0:5][]
           | "\(.price_str)\t\(.merchant.name)\t\(.title)"'
```

To narrow to the actual product, filter out accessory titles first:

```bash
  ... | jq -r '[.results.results.organic[]
       | select(.title | test("skin|wrap|case|cover|grip|protector"; "i") | not)]
       | sort_by(.price) | .[0] | "\(.price_str) — \(.merchant.name)"'
```

## 3. Record a price over time (NDJSON log)

Append one timestamped line per check; the file becomes your time series.

```bash
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
price=$(decodo amazon-pricing B09H74FXNW --parse | jq -r '.results.pricing[0].price')
printf '{"ts":"%s","sku":"B09H74FXNW","price":%s}\n' "$ts" "$price" >> prices.ndjson
```

## 4. Detect a drop

Compare the two most recent records:

```bash
tail -2 prices.ndjson | jq -s 'if (.[1].price < .[0].price)
  then "DROP \(.[0].price) → \(.[1].price)" else "no drop (\(.[1].price))" end'
```

Schedule step 3 (e.g. a cron job) to build history; run step 4 after each append to alert.

## Tips & gotchas

- Keep `--geo` (and `--currency` on Amazon) **fixed across runs** so prices stay comparable —
  storefront/locale changes both price and availability.
- `price` is a number; `price_str` keeps the currency symbol (e.g. `$79.99`), `price_old` is the
  pre-discount price when present.
- Out-of-stock or blocked variants may omit `price` — guard jq with `// empty` or `// "n/a"`.
- Exit 5 (rate limited) → lower frequency / back off. Exit 3 (auth) → recheck the token (see
  decodo-web-scraping). Exit codes are listed in that skill.

## Links

- Setup, surfaces, output handling: the **decodo-web-scraping** skill
- Targets & parameters: <https://help.decodo.com/docs/web-scraping-api-targets>
