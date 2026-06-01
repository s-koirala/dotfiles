# MCP Server Templates

Each JSON file is a reference invocation for a community MCP server. Dotfiles do NOT auto-register servers — per-machine control avoids unwanted auth prompts on shared machines.

To register on a given machine, run the command in each file's `_register` field. Example:

```
claude mcp add --transport stdio --scope user arxiv -- uvx arxiv-mcp-server
```

## Templates

- `arxiv.json` — literature search, used by `literature-check` agent. **Active.** PyPI: `arxiv-mcp-server`.
- `filesystem.json` — scoped filesystem access outside project cwd. **Active.** npm: `@modelcontextprotocol/server-filesystem` (official).

## Secrets
Never put tokens in `env:` directly in a registered MCP server. Use `apiKeyHelper` in `~/.claude/settings.local.json` pointing to an OS keychain script (`security find-generic-password` macOS, `pass` Linux, `cmdkey`/Credential Manager Windows).

## Adding more
Canonical registry: https://github.com/modelcontextprotocol/servers plus the Anthropic MCP registry at `https://api.anthropic.com/mcp-registry/v0/servers`. Drop a new `<name>.json` file here following the same structure.
