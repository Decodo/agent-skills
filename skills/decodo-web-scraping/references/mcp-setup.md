# Decodo MCP setup (per client)

Use this when the host has **no shell** (Claude Desktop, claude.ai) or when you prefer tool-call
native scraping over the CLI. Decodo's MCP server is hosted at `https://mcp.decodo.com/mcp` and
authenticates with the same Web Scraping API **basic auth token** used everywhere else
(`Authorization: Basic <token>`). Get a token at <https://dashboard.decodo.com/playground>
(free tier: ~2K requests, no card).

## Hosted server — generic config

Most MCP clients accept a remote server by URL + headers. Add:

```json
{
  "mcpServers": {
    "Decodo": {
      "url": "https://mcp.decodo.com/mcp",
      "headers": { "Authorization": "Basic <basic_auth_token>" }
    }
  }
}
```

### Toolsets (optional, recommended)

The server exposes ~30 tools across five toolsets: `web`, `search`, `ecommerce`,
`social_media`, `ai`. Enabling only what you need keeps tool selection clean and the agent
faster. On the hosted URL, scope with a query param:

```
https://mcp.decodo.com/mcp?toolsets=web,search
```

## Per-client steps

### Claude Code (CLI clients)

If a shell is available, prefer the `decodo` CLI (see the main skill). If you specifically want
MCP in Claude Code:

```bash
claude mcp add --transport http Decodo https://mcp.decodo.com/mcp \
  --header "Authorization: Basic <basic_auth_token>"
```

### Claude Desktop

1. Settings → Developer → Edit Config (`claude_desktop_config.json`).
2. Add the local (npx) server — Claude Desktop runs it as a subprocess:

   ```json
   {
     "mcpServers": {
       "Decodo": {
         "command": "npx",
         "args": ["-y", "@decodo/mcp-server"],
         "env": {
           "SCRAPER_API_TOKEN": "<basic_auth_token>",
           "TOOLSETS": "web,ai"
         }
       }
     }
   }
   ```
3. Save and restart Claude Desktop.

### Cursor

1. Settings → MCP → **Add a new global MCP server** (opens `mcp.json`).
2. Paste the hosted generic config above.
3. Save — look for a green status indicator next to **Decodo**.

One-click install deeplink is also on the [MCP server README](https://github.com/Decodo/mcp-server).

### Windsurf

1. Settings → Windsurf Settings → Cascade → **Add custom server +** (opens `mcp_config.json`).
2. Paste the hosted generic config above.
3. Save and restart Windsurf.

## Self-host / local

Run the server yourself instead of using the hosted endpoint:

```bash
npx -y @decodo/mcp-server          # quick, with SCRAPER_API_TOKEN in env
```

Or clone and build from <https://github.com/Decodo/mcp-server> and point your client at
`build/index.js` via the `command`/`args` form.

## Verify

In the client, prompt:

> "Scrape the titles of the top 5 articles from Hacker News"

A structured list back within seconds means it's wired up. An auth error means the token is
wrong or missing — recheck it in the dashboard.
