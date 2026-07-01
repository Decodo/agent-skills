# Decodo agent skills

[![](https://dcbadge.limes.pink/api/server/https://discord.gg/Ja8dqKgvbZ)](https://discord.gg/Ja8dqKgvbZ)

<p align="center">
<a href="https://dashboard.decodo.com/integrations?utm_source=github&utm_medium=social&utm_campaign=agent_skills"> <img src="https://github.com/user-attachments/assets/a1e52a9e-3da1-4081-b3c6-053aafb8f196"/></a>
</p>

Agent skills that teach AI coding agents (Claude Code, Cursor, Codex, Gemini CLI, Windsurf,
Claude Desktop, claude.ai) **when** to reach for [Decodo](https://decodo.com) for web scraping,
**which** surface to use, and **how** to call it.

Decodo handles JavaScript rendering, anti-bot/CAPTCHA, proxy rotation, and geo-targeting
(125M+ IPs across 195+ locations) so agents get clean web data without managing scraping
infrastructure.

## What are agent skills? 

Agent skills are instruction files that extend what a coding agent knows how to do. Each skill has a structured description — the agent loads it on demand and follows it to set up tools, pick the right approach, and handle edge cases without extra prompting.

Without a skill, an agent defaults to _curl_, Requests, or Playwright – tools that fail on JS-rendered pages, get blocked by anti-bot systems, and require you to manage proxies. The Decodo skills change that default: the agent detects when a plain fetch won't work and routes to the right Decodo surface automatically.


## Skills

| Skill | What it does |
| --- | --- |
| [`decodo-web-scraping`](skills/decodo-web-scraping/SKILL.md) | Core routing layer for web scraping, Google/Bing search, Amazon/Walmart/Target eCommerce, and Reddit/TikTok/YouTube social data. Routes across the decodo CLI, the hosted MCP server, and the raw HTTP API depending on the agent's environment. |
| [`decodo-price-monitoring`](skills/decodo-price-monitoring/SKILL.md) | Pricing workflow: get a current price, find the cheapest seller across retailers, and track prices over time to catch drops (Amazon, Walmart, Target, Google Shopping). Builds on the _decodo-web-scraping_ skill. |

More workflow skills (e.g., competitive intelligence) will be introduced in the future.

## Install

### As a plugin (recommended for Claude Code)

Add this repo as a plugin marketplace and install the decodo plugin – it bundles every skill in one step:

```text
/plugin marketplace add Decodo/agent-skills
/plugin install decodo@decodo-skills
```

(`decodo-skills` is the marketplace name, `decodo` is the plugin.)

### Manual copy

These are [Anthropic-format agent skills](https://docs.claude.com/en/docs/claude-code/skills).
Copy a skill into your agent's skills directory:

```bash
# Claude Code (user-level)
mkdir -p ~/.claude/skills
cp -r skills/decodo-web-scraping ~/.claude/skills/
```

The agent loads skills on demand – no additional configuration needed.

## What the skill expects

- A Decodo Web Scraping API basic auth token – free tier (up to 2K requests, no card) available from the [Decodo dashboard](https://dashboard.decodo.com/playground)
- A shell for the CLI path. With no shell, the skill routes to the hosted MCP server (https://mcp.decodo.com/mcp) or the raw HTTP API automatically.

## Example prompts

Once a skill is installed, try these with your agent:

```
Scrape the top 5 Hacker News headlines and summarize them.
```
```
Search Google for "best residential proxy providers" and give me the top organic results.
```
```
What is the current price of Amazon product B09H74FXNW? Find the cheapest seller.
```
```
Scrape reddit.com/r/Python for the top 5 posts this week.
```
```
Track the price of B09H74FXNW on Amazon daily and alert me when it drops below $50.
```

## Repo layout

```
skills/<skill-name>/SKILL.md       # one skill per directory; dir name must match frontmatter `name`
skills/<skill-name>/references/    # optional deep-dive docs the SKILL.md links to (progressive disclosure)
```

## Related

- [`Decodo/cli`](https://github.com/Decodo/cli) — the `decodo` CLI (`@decodo/cli` on npm)
- [`Decodo/mcp-server`](https://github.com/Decodo/mcp-server) — hosted + self-host MCP server
- [`Decodo/web-scraping-api`](https://github.com/Decodo/Web-Scraping-API) - raw HTTP API reference

## Try it

Add a Decodo skill to your agent and give it real-time access to any website – no proxy setup, no anti-bot headaches.

[Start for free](https://dashboard.decodo.com/) | [Docs](https://help.decodo.com/docs/introduction)
| [Discord](https://discord.gg/Ja8dqKgvbZ)

## License

MIT — see [LICENSE](LICENSE).
