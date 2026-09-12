# anki-multidefine-mcp

MCP server exposing [MultiDefine](https://github.com/thegeneralist01/anki-multidefine)'s
monolingual dictionary providers as tools. An AI agent (Claude, GPT, or any
MCP-capable client) can look up words in English, German, Russian, French, and
Azerbaijani dictionaries and receive structured definitions, IPA phonetics,
audio URLs, and verb forms — ready to be added as Anki flashcards via
[anki-mcp-server](https://github.com/scambier/mcp-server-anki).

## Prerequisites

- Python 3.10+
- [anki-mcp-server](https://github.com/scambier/mcp-server-anki) installed and running (for the Anki integration)
- The [MultiDefine Anki add-on](https://github.com/thegeneralist01/anki-multidefine) installed in Anki (creates the required note types)

## Install

```bash
pip install anki-multidefine-mcp
```

## Claude Desktop configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "anki-multidefine": {
      "command": "anki-multidefine-mcp"
    }
  }
}
```

## Exposed tools

| Tool | Description |
|------|-------------|
| `define(word, language)` | Look up a word in a monolingual dictionary. Returns definitions, IPA, audio URL, verb forms. |
| `languages()` | List supported language keys and their capabilities (audio, IPA, verb forms). |

## Exposed resource

| URI | Description |
|-----|-------------|
| `multidefine://schema` | Field mapping and workflow rules for adding MultiDefine cards to Anki via anki-mcp-server. |

## Supported languages

| Key | Dictionary |
|-----|------------|
| `english` | Oxford Learner's Dictionaries |
| `german` | DWDS |
| `russian` | ru.Wiktionary |
| `french` | Larousse |
| `azerbaijani` | AZLEKS |

## Example prompt

> Read `multidefine://schema`, then look up "Haus" in German, download the
> audio into Anki, and add a MultiDefine_German note to my "German" deck.
