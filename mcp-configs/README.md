# MCP Configurations

Model Context Protocol configurations for connecting AI assistants to legal tools and data sources.

## What is MCP?

MCP (Model Context Protocol) allows AI assistants like Claude to connect to external tools and databases. For legal work, this enables:

- Querying legal databases (EUR-Lex, CourtListener)
- Accessing document management systems
- Connecting to legal research platforms

## Available Configurations

### Claude Desktop

Ready-to-use configurations for Claude Desktop:

| Config | Tools | Use Case |
|--------|-------|----------|
| [legal-research.json](./claude-desktop/legal-research.json) | EUR-Lex, CourtListener | Legal research |
| [document-management.json](./claude-desktop/document-management.json) | Google Drive, filesystem | File access |
| [full-legal-stack.json](./claude-desktop/full-legal-stack.json) | All tools combined | Complete setup |

### Server Guides

Setup guides for MCP servers:
- [CourtListener MCP](./server-guides/courtlistener-mcp.md)
- [EUR-Lex MCP](./server-guides/eurlex-mcp.md)
- [Google Drive for Legal](./server-guides/google-drive-legal.md)

## Installation

### macOS

1. Open Claude Desktop settings
2. Navigate to Developer → MCP Servers
3. Add configuration:

