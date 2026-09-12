# anki-multidefine-mcp

Tell Claude to add a word to Anki. It looks it up in a real monolingual dictionary, formats the card, downloads audio, and creates the note — all in one message.

```
"Add a card for 'Schadenfreude' to my German deck."
```

Works for English, German, Russian, French, and Azerbaijani. Definitions come from Oxford, DWDS, Wiktionary, and Larousse — the same sources the [MultiDefine Anki add-on](https://github.com/thegeneralist01/anki-multidefine) uses.

---

## What you need before starting

| Requirement | How to get it |
|---|---|
| [Anki](https://apps.ankiweb.net) desktop app | Download from ankiweb.net |
| [AnkiConnect](https://ankiweb.net/shared/info/2055492827) Anki add-on | Install code `2055492827` in Anki |
| [MultiDefine](https://github.com/thegeneralist01/anki-multidefine) Anki add-on | Provides the note types Claude writes to |
| [Node.js](https://nodejs.org) 22+ | For the Anki MCP server |
| Python 3.10+ | For this package |
| [Claude Desktop](https://claude.ai/download) | The AI client |

---

## Setup

### Step 1 — Install the Anki add-ons

Open Anki → Tools → Add-ons → Get Add-ons and install both codes:

- `2055492827` — AnkiConnect (lets Claude talk to Anki)
- `(MultiDefine code from the repo above)` — creates the note types

Restart Anki after installing.

### Step 2 — Install this package

```bash
pip install anki-multidefine-mcp
```

### Step 3 — Configure Claude Desktop

Open (or create) `~/Library/Application Support/Claude/claude_desktop_config.json` and paste:

```json
{
  "mcpServers": {
    "anki-multidefine": {
      "command": "anki-multidefine-mcp"
    },
    "anki-mcp": {
      "command": "npx",
      "args": ["-y", "@ankimcp/anki-mcp-server", "--stdio"],
      "env": {
        "ANKI_CONNECT_URL": "http://localhost:8765"
      }
    }
  }
}
```

### Step 4 — Restart Claude Desktop and Anki

Make sure Anki is open (AnkiConnect only responds while Anki is running).

---

## Quick prompts to try

Copy any of these directly into Claude:

```
Add a card for "Haus" to my German deck.
```

```
Look up "schadenfreude" in English and add it to my Vocabulary deck.
```

```
Add cards for these Russian words to my Russian deck: уважение, доверие, свобода.
```

```
What German words have I added in the last week?
```

---

## How it works

When you ask Claude to add a word, it:

1. Calls `define(word, language)` — looks up the word in the monolingual dictionary
2. Reads `multidefine://schema` — knows exactly which Anki fields to fill and how
3. Calls anki-mcp-server's `findNotes` — skips the card if it already exists
4. Calls `storeMediaFile` with the audio URL — downloads pronunciation into Anki's media folder
5. Calls `addNote` with the `MultiDefine_{Language}` note type — card appears in your deck

No UI to learn. No form to fill. Just describe what you want.

---

## Supported languages

| Key | Dictionary | Audio | IPA | Verb forms |
|---|---|---|---|---|
| `english` | Oxford Learner's | Yes | Yes | Yes |
| `german` | DWDS | Yes | Yes | Yes |
| `russian` | ru.Wiktionary | Yes | Yes | — |
| `french` | Larousse | Yes | — | — |
| `azerbaijani` | AZLEKS | — | — | — |

---

## Troubleshooting

**"Cannot connect to Anki"** — Anki must be open and AnkiConnect installed. Visit `http://localhost:8765` in your browser; you should see `AnkiConnect`.

**"Note type not found"** — The MultiDefine Anki add-on must be installed so the `MultiDefine_German` (etc.) note types exist. Open Anki → Tools → Manage Note Types to confirm.

**"Word not found"** — The word isn't in that dictionary. Try a different language key or check spelling.

**Card already exists** — Claude will tell you and skip creation. Ask it to update the existing card if you want.

---

## MCP tools exposed

| Tool | Description |
|---|---|
| `define(word, language)` | Look up a word. Returns definitions, IPA, audio URL, verb forms. |
| `languages()` | List supported language keys and their capabilities. |

**Resource:** `multidefine://schema` — field mapping and workflow rules Claude reads before creating notes.

---

## For developers

See [AGENTS.md](AGENTS.md) for the provider contract, word_info schema, and instructions for adding a new language.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, smoke tests, and PR checklist.

**License:** GPL v2. `providers/oxford.py` is BSD 3-Clause (Near Huscarl).
