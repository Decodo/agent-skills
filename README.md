# Decodo agent skills

Agent skills that teach AI coding agents (Claude Code, Cursor, Codex, Gemini CLI, Windsurf,
Claude Desktop, claude.ai) **when** to reach for [Decodo](https://decodo.com) for web scraping,
**which** surface to use, and **how** to call it.

Decodo handles JavaScript rendering, anti-bot/CAPTCHA, proxy rotation, and geo-targeting
(125M+ IPs across 195+ locations) so agents get clean web data without managing scraping
infrastructure.

## Skills

| Skill | What it does |
| --- | --- |
| [`decodo-web-scraping`](skills/decodo-web-scraping/SKILL.md) | Routing layer for scraping, search (Google/Bing), e-commerce (Amazon/Walmart/Target), and social (Reddit/TikTok/YouTube). Routes across the `decodo` CLI, the hosted MCP server, and the raw HTTP API. |

More skills (workflow recipes like price monitoring and competitive intel) will follow.

## Install

These are [Anthropic-format agent skills](https://docs.claude.com/en/docs/claude-code/skills).
Copy a skill into your agent's skills directory:

```bash
# Claude Code (user-level)
mkdir -p ~/.claude/skills
cp -r skills/decodo-web-scraping ~/.claude/skills/
```

The agent loads the skill on demand based on its `description`, then follows it to set up and
call Decodo. The skill leads with `npx @decodo/cli`, so an agent can start scraping with zero
install once a token is configured.

## What the skill expects

- A Decodo Web Scraping API basic auth token — free tier (up to 2K requests, no card) at
  <https://dashboard.decodo.com/playground>.
- A shell for the CLI path. With no shell, the skill routes to the hosted MCP server
  (`https://mcp.decodo.com/mcp`) or the raw HTTP API.

## Repo layout

```
skills/<skill-name>/SKILL.md   # one skill per directory; dir name must match frontmatter `name`
```

## Related

- [`Decodo/cli`](https://github.com/Decodo/cli) — the `decodo` CLI (`@decodo/cli` on npm)
- [`Decodo/mcp-server`](https://github.com/Decodo/mcp-server) — hosted + self-host MCP server

## License

MIT — see [LICENSE](LICENSE).
