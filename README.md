# anki-multidefine-mcp

Tell Claude to add a word to Anki. It looks it up in a real monolingual dictionary, formats the card, downloads audio, and creates the note — all in one message.

```
"Add a card for 'Schadenfreude' to my German deck."
```

Works for English, German, Russian, French, and Azerbaijani. Definitions come from Oxford, DWDS, Wiktionary, and Larousse — the same sources the [MultiDefine Anki add-on](https://github.com/thegeneralist01/anki-multi-language-auto-define) uses.

---

## What you need before starting

| Requirement | Notes |
|---|---|
| [Anki](https://apps.ankiweb.net) desktop app | Free, runs locally |
| [AnkiConnect](https://ankiweb.net/shared/info/2055492827) add-on | Lets Claude talk to Anki |
| [MultiDefine](https://github.com/thegeneralist01/anki-multi-language-auto-define) add-on | Provides the note types Claude writes to |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Runs this server — no separate install step needed |
| [Claude Desktop](https://claude.ai/download) | The AI client |

---

## Setup

### Step 1 — Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or via Homebrew: `brew install uv`

### Step 2 — Install the Anki add-ons

Open Anki → **Tools → Add-ons → Get Add-ons** and enter:

```
2055492827
```

That installs AnkiConnect. Then install MultiDefine:

1. Download **[multidefine.ankiaddon](https://github.com/thegeneralist01/anki-multi-language-auto-define/releases/latest/download/multidefine.ankiaddon)**
2. In Anki: **Tools → Add-ons → Install from file** → select the downloaded file

Restart Anki after both are installed.

### Step 3 — Configure Claude Desktop

Open (or create) this file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Paste the following (merge with any existing `mcpServers` block if you have one):

```json
{
  "mcpServers": {
    "anki-multidefine": {
      "command": "uvx",
      "args": ["anki-multidefine-mcp"]
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

### Step 4 — Restart Claude Desktop

Keep Anki open — AnkiConnect only responds while Anki is running.

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
3. Calls `findNotes` — skips the card if it already exists in the deck
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

Claude infers the language from context — you rarely need to specify the key explicitly.

---

## Troubleshooting

**Claude says it can't connect to Anki** — Anki must be open and AnkiConnect installed. Verify by visiting `http://localhost:8765` in your browser; you should see a plain-text `AnkiConnect` response.

**"Note type not found"** — MultiDefine must be installed in Anki so the `MultiDefine_German` (etc.) note types exist. Check via **Tools → Manage Note Types**.

**"Word not found"** — The word isn't in that dictionary. Try a different spelling or language.

**Duplicate card** — Claude checks first and tells you if the card already exists. Ask it to update the existing note if you want.

**`uvx` not found** — Claude Desktop may not inherit your shell PATH. Use the full path: run `which uvx` in your terminal, then replace `"uvx"` in the config with that path (e.g. `/Users/you/.local/bin/uvx`).

---

## MCP tools exposed

| Tool | Description |
|---|---|
| `define(word, language)` | Look up a word. Returns definitions, IPA, audio URL, verb forms. |
| `languages()` | List supported language keys and their capabilities. |

**Resource:** `multidefine://schema` — field mapping and workflow rules Claude reads automatically before creating notes.

---

## For developers

See [AGENTS.md](AGENTS.md) for the provider contract, word_info schema, and instructions for adding a new language.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, smoke tests, and PR checklist.

**License:** GPL v2. `providers/oxford.py` is BSD 3-Clause (Near Huscarl).
